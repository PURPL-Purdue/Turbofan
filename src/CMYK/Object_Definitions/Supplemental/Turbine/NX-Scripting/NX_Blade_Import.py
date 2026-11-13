# Automates sheet-surface generation from XYZ text files in Siemens NX.
# Original program logic is unchanged; comments explain its operation.
import os
import NXOpen
import NXOpen.Features
import NXOpen.GeometricUtilities


# Read and preprocess coordinate data before creating NX geometry.
class PointFileReader:

    def __init__(self, folderPath):
        self.folderPath = folderPath


    # Return sections as (filename, list of XYZ tuples).
    def readFiles(self):

        allSections = []

        # Sorting keeps the cross-section order deterministic.
        fileNames = sorted(os.listdir(self.folderPath))

        for fileName in fileNames:

            # Ignore all files except text files.
            if not fileName.lower().endswith(".txt"):
                continue

            filePath = os.path.join(
                self.folderPath,
                fileName
            )

            sectionPoints = []

            with open(filePath, "r") as file:

                for line in file:

                    # Whitespace-separated input: X Y Z; ignore extra columns.
                    values = line.split()

                    # Skip malformed or incomplete coordinate lines.
                    if len(values) < 3:
                        continue

                    try:
                        x = float(values[0])
                        y = float(values[1])
                        z = float(values[2])

                    except ValueError:
                        continue

                    sectionPoints.append(
                        (x, y, z)
                    )

            # A valid spline section needs at least two coordinates.
            if len(sectionPoints) >= 2:

                # Sample roughly 500 points to reduce NX computational load.
                # This is not a strict 500-point cap for arbitrary file sizes.
                step = max(
                    1,
                    len(sectionPoints) // 500
                )

                reducedPoints = sectionPoints[::step]

                # Retain the exact endpoint even when sampling skips it.
                if reducedPoints[-1] != sectionPoints[-1]:
                    reducedPoints.append(
                        sectionPoints[-1]
                    )

                allSections.append(
                    (fileName, reducedPoints)
                )

        return allSections


# Create cubic splines and loft a sheet through them using NXOpen.
class NXGeometryBuilder:

    def __init__(self):

        # Obtain the active NX session, working part, and output window.
        self.session = NXOpen.Session.GetSession()
        self.workPart = self.session.Parts.Work
        self.listingWindow = self.session.ListingWindow


    # Create one nonperiodic degree-3 spline passing through XYZ points.
    def createSpline(self, points):

        splineBuilder = (
            self.workPart.Features
            .CreateStudioSplineBuilderEx(
                NXOpen.Features.StudioSpline.Null
            )
        )

        splineBuilder.Type = (
            NXOpen.Features
            .StudioSplineBuilderEx
            .Types
            .ThroughPoints
        )

        splineBuilder.Degree = 3
        splineBuilder.IsPeriodic = False

        # Each point is an NX object constrained into the spline builder.
        for x, y, z in points:

            nxPoint = (
                self.workPart.Points
                .CreatePoint(
                    NXOpen.Point3d(
                        x,
                        y,
                        z
                    )
                )
            )

            constraint = (
                splineBuilder
                .ConstraintManager
                .CreateGeometricConstraintData()
            )

            constraint.Point = nxPoint

            splineBuilder.ConstraintManager.Append(
                constraint
            )

        # Commit creates the NX feature; extract its curve and free builder.
        splineBuilder.Commit()

        spline = splineBuilder.Curve

        splineBuilder.Destroy()

        return spline


    # Build a spline for each file, preserving its source points.
    def createAllSplines(self, allSections):

        splines = []

        for fileName, points in allSections:

            self.listingWindow.WriteLine(
                "Creating spline from: "
                + fileName
            )

            spline = self.createSpline(
                points
            )

            splines.append(
                (spline, points)
            )

        return splines


    # Use the ordered splines as sections for a Through Curves sheet.
    def createSurface(self, splines):

        throughBuilder = (
            self.workPart.Features
            .CreateThroughCurvesBuilder(
                NXOpen.Features.Feature.Null
            )
        )

        # Sheet preference creates a surface body, not a solid body.
        throughBuilder.BodyPreference = (
            NXOpen.Features
            .ThroughCurvesBuilder
            .BodyPreferenceTypes
            .Sheet
        )

        # Allow NX to adjust the intermediate surface shape as needed.
        throughBuilder.PreserveShape = False

        # Configure geometric tolerances for alignment and sections.
        throughBuilder.Alignment.AlignCurve.DistanceTolerance = 0.01
        throughBuilder.Alignment.AlignCurve.ChainingTolerance = 0.0095
        throughBuilder.Alignment.AlignCurve.AngleTolerance = 0.5

        throughBuilder.SectionTemplateString.DistanceTolerance = 0.01
        throughBuilder.SectionTemplateString.ChainingTolerance = 0.0095
        throughBuilder.SectionTemplateString.AngleTolerance = 0.5

        # Match spline sections by curve parameterization.
        throughBuilder.Alignment.AlignType = (
            NXOpen.GeometricUtilities
            .AlignmentMethodBuilder
            .Type
            .Parameter
        )

        # Convert each spline into an NX Section used by the loft.
        for spline, points in splines:

            section = (
                self.workPart.Sections
                .CreateSection(
                    0.01,
                    0.0095,
                    0.5
                )
            )

            section.SetAllowedEntityTypes(
                NXOpen.Section
                .AllowTypes
                .OnlyCurves
            )

            # Disallow self-intersecting and degenerate section curves.
            section.AllowSelfIntersection(
                False
            )

            section.AllowDegenerateCurves(
                False
            )

            # Select the already-created spline as a section curve.
            rule = (
                self.workPart
                .ScRuleFactory
                .CreateRuleCurveDumb(
                    [spline]
                )
            )

            # Use the section's first input point as the help point.
            # This avoids the unsupported spline.EvaluatePoint call.
            x, y, z = points[0]

            helpPoint = NXOpen.Point3d(
                x,
                y,
                z
            )

            section.AddToSection(
                [rule],
                spline,
                NXOpen.NXObject.Null,
                NXOpen.NXObject.Null,
                helpPoint,
                NXOpen.Section.Mode.Create,
                False
            )

            # Append sections in file order to define the loft sequence.
            throughBuilder.SectionsList.Append(
                section
            )

        # Commit the Through Curves feature, then dispose of the builder.
        surface = (
            throughBuilder.CommitFeature()
        )

        throughBuilder.Destroy()

        return surface


# Orchestrate input, progress logging, curve creation, and surfacing.
def main():

    # Folder containing the .txt coordinate files on the NX machine.
    folderPath = os.path.expanduser(
        "~/Downloads/NXTestPoints"
    )

    session = NXOpen.Session.GetSession()

    listingWindow = session.ListingWindow
    listingWindow.Open()

    reader = PointFileReader(
        folderPath
    )

    allSections = reader.readFiles()

    # Report file counts and retained point counts to NX's listing window.
    listingWindow.WriteLine(
        "Files read: "
        + str(len(allSections))
    )

    totalPoints = 0

    for fileName, points in allSections:

        listingWindow.WriteLine(
            fileName
            + ": "
            + str(len(points))
            + " points after reduction"
        )

        totalPoints += len(points)

    listingWindow.WriteLine(
        "Total points used: "
        + str(totalPoints)
    )

    # Through Curves requires at least two section curves.
    if len(allSections) < 2:

        listingWindow.WriteLine(
            "ERROR: Need at least two files."
        )

        return

    # Create a curve for each section, then loft a single sheet surface.
    geometryBuilder = NXGeometryBuilder()

    splines = (
        geometryBuilder
        .createAllSplines(
            allSections
        )
    )

    listingWindow.WriteLine(
        "Splines created: "
        + str(len(splines))
    )

    geometryBuilder.createSurface(
        splines
    )

    listingWindow.WriteLine(
        "Through Curves surface created."
    )


# Run only when this Python file is executed as the main script.
if __name__ == "__main__":
    main()
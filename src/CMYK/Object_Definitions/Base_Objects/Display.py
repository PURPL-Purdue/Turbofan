from pathlib import Path
from .Engine import Engine
from .Flow import Flow

class Display:
    def __init__(self, Engine: Engine) -> None:
        self.Engine = Engine
        self.DIVIDER_WIDTH = 64

    @staticmethod
    def generateDivider(width: int, title : str) -> str:
        line1 = line3 = "#" * width
        formattedUpperTitle = (" ".join(title.upper().split()))
        line2 = f"{formattedUpperTitle:^{width}s}"
        return "\n".join([line1, line2, line3])
        
    def plotGraphs(self) -> None:
        pass

    def textOutput(self, outputFile : Path) -> None:
        with open(outputFile, "w") as txt:
            self.CYAN_textOutput(txt)
    
    def plotOutput(self):
        pass

    

    def CYAN_textOutput(self, txt):
        # Set column widths
        SnumWidth = 4
        nameWidth = 12
        dWidth = 14
        dPrecs = 3


        # Format table header, get width
        header = f"\n\n{"S##":>{SnumWidth}s}{"STATION NAME":^{nameWidth*2+1}s}{"T0 (K)":>{dWidth}s}{"P0 (Pa)":>{dWidth}s}{"T (K)":>{dWidth}s}{"P (Pa)":>{dWidth}s}\n"
        
        # Print "CYCLE ANALYSIS" DIVIDER
        txt.write(self.generateDivider(len(header)-2, "CYCLE ANALYSIS"))

        # Print table header
        txt.write(header)
        txt.write("=" * (len(header)-2) + "\n")

        # Print flowstation properties
        for compName, compObj in self.Engine.flowpath.items():
            for flowName, flowObj in vars(compObj).items():
                T = f"{flowObj.T:{dWidth}.{dPrecs}f}" if (getattr(flowObj, 'T', None) is not None) else "N/A"
                P = f"{flowObj.P:{dWidth}.{dPrecs}f}" if (getattr(flowObj, 'P', None) is not None) else "N/A"
                if isinstance(flowObj, Flow):
                    dataLine = f"{flowObj.name:>{SnumWidth}s}{compName:>{nameWidth}s} {flowName:<{nameWidth}s}"\
                            f"{flowObj.T0:{dWidth}.{dPrecs}f}{flowObj.P0:{dWidth}.{dPrecs}f}"\
                            f"{T:>{dWidth}s}{P:>{dWidth}s}\n"
                    txt.write(dataLine)
            txt.write("-" * len(dataLine) + "\n")
        
        # GROUP CYCLE ANALYSIS OUTPUT BY STATION (deals with duplicates) NOT USED ---------------------------------------------------
        # elif (groupType == "BY_STATION"):
        #     dataLines = {}
        #     for compName, compObj in self.Engine.flowpath.items():
        #         for flowName, flowObj in vars(compObj).items():
        #             if isinstance(flowObj, Flow):
        #                 dataLines[flowObj.name] = f"{flowObj.name:>{SnumWidth}s}{compName:>{nameWidth}s} {flowName:<{nameWidth}s}"\
        #                                         f"{flowObj.T0:{dWidth}.{dPrecs}f}{flowObj.P0:{dWidth}.{dPrecs}f}\n"
        #     dataLines = {Snum: dataLines[Snum] for Snum in sorted(dataLines)}

            
        #     lastStation : str = None
        #     for Snum in dataLines:
        #         if (Snum != lastStation):
        #             txt.write(dataLines[Snum])
        #             lastStation = Snum
        #         else:
        #             txt.write(dataLines[Snum])
        #             txt.write("-" * len(dataLine) + "\n")
        #             lastStation = Snum

        #             # if (flowObj.name != lastStation):
        #             #     dataLine = f"{flowObj.name:>{SnumWidth}s}{compName:>{nameWidth}s} {flowName:<{nameWidth}s}"\
        #             #             f"{flowObj.T0:{dWidth}.{dPrecs}f}{flowObj.P0:{dWidth}.{dPrecs}f}\n"
        #             #     txt.write(dataLine)
        #             #     lastStation = flowObj.name
        #             # else:
        #             #     dataLine = f"{" ":>{SnumWidth}s}{compName:>{nameWidth}s} {flowName:<{nameWidth}s}"\
        #             #             f"{" ":{dWidth}s}{" ":{dWidth}s}\n"
        #             #     txt.write(dataLine)
        #             #     txt.write("-" * len(dataLine) + "\n")
        #             #     lastStation = flowObj.name

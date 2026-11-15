from pathlib import Path

from Object_Definitions.Components import AxialTurbine
from Object_Definitions.Base_Objects import ComponentBase


def print_turbine_results(turbine):
    """Print the preliminary sizing results for one turbine."""

    print("\n" + "=" * 65)
    print(f" {turbine.name} TURBINE SIZING RESULTS")
    print("=" * 65)

    print(f"Operating RPM:           {turbine.operating_rpm:.2f}")
    print(f"Number of stages:        {turbine.num_stages}")
    print(f"Required turbine power: {turbine.required_power_W / 1e6:.4f} MW")

    generated_power = turbine.pitchline_res.total_power_generated

    print(f"Generated turbine power: {generated_power / 1e6:.4f} MW")

    print(f"Power margin:            {turbine.pitchline_res.excess_power_margin:.3f} %")

    print("\nANNULUS GEOMETRY")
    print("-" * 65)

    annulus = turbine.annulus_res

    for i in range(annulus["num_stations"]):

        print(
            f"Station {i + 1:02d}: Hub = {annulus['r_hub'][i]:.5f} m | Mean = {annulus['r_mean'][i]:.5f} m | Tip = {annulus['r_tip'][i]:.5f} m")

    print("\n" + "=" * 65)


def main():
    # -----------------------------------------------------
    #                  CONFIG
    # -----------------------------------------------------

    project_root = Path(__file__).resolve().parent.parent
    config_path = (project_root / "Config_Files" / "Config_001.yaml")

    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    ComponentBase.load_config(config_path)

    HPT = AxialTurbine("HPT")
    LPT = AxialTurbine("LPT")

    # Each turbine reads its own configuration section.
    HPT.config()
    LPT.config()

    # -----------------------------------------------------
    #               VALIDATION
    # -----------------------------------------------------
    if not HPT.standalone:
        raise RuntimeError("HPT standalone mode is not enabled in the YAML.")

    if not LPT.standalone:
        raise RuntimeError("LPT standalone mode is not enabled in the YAML.")

    # -----------------------------------------------------
    #               RUN MEANLINES
    # -----------------------------------------------------
    print("\nStarting HPT preliminary sizing...")
    HPT.MAGENTA()

    print("HPT sizing completed.")
    print_turbine_results(HPT)


    print("\nStarting LPT preliminary sizing...")
    LPT.MAGENTA()

    print("LPT sizing completed.")
    print_turbine_results(LPT)

    # -----------------------------------------------------
    #                  FINAL SUMMARY
    # -----------------------------------------------------

    print("\n" + "=" * 65)
    print(" TURBINE SIZING SUMMARY")
    print("=" * 65)

    print(f"HPT: {HPT.operating_rpm:.1f} RPM | {HPT.num_stages} stages | {HPT.required_power_W / 1e6:.3f} MW")

    print(f"LPT: {LPT.operating_rpm:.1f} RPM | {LPT.num_stages} stages | {LPT.required_power_W / 1e6:.3f} MW (Required)")
    print("=" * 65)

    # Return instances so they can also be inspected
    # interactively if main() is imported and called.
    return HPT, LPT

if __name__ == "__main__":
    HPT, LPT = main()

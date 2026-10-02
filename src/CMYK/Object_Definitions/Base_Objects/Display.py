import sys
from pathlib import Path
from datetime import datetime
import getpass
import tomllib
from pint import UnitRegistry, Quantity, UndefinedUnitError, DimensionalityError
from .Flow import Flow

from CMYK.Object_Definitions.Components.Shaft import Shaft
from CMYK.Object_Definitions.Components.Start import Start
from CMYK.Object_Definitions.Components.End import End
from CMYK.Object_Definitions.Components.Burner import Burner
from .Compressor import Compressor
from .ComponentBase import ComponentBase

UR = UnitRegistry()
_NONDIM = 'dimensionless'

class Display:
    def __init__(self, engine) -> None:
        self.Engine = engine
        self.DIVIDER_WIDTH = 64

        self.verbose = None
        self.standalone_dataline_title_width = 24
        self.standalone_dataline_data_width = 12
        self.standalone_dataline_data_precision = 3

    @staticmethod
    def generateDivider(width: int, title : str) -> str:
        # line1 = line3 = "#" * width
        formattedUpperTitle = (" ".join(title.upper().split()))
        # line2 = f"{formattedUpperTitle:^{width}s}"

        line1 = line3 = "-" * width
        line2 = f"{' ':40s}{formattedUpperTitle}"
        return "\n".join([line1, line2, line3]) + "\n\n"

    @staticmethod
    def standalone_block_header(title):
        width = OutVarCYAN.title_width + OutVarCYAN.data_width + 10
        return title + ' ' + '-' * (width - len(title)) + '\n'

    # ----------------------------------------------------------------------------
    #                               MAIN FUNCTIONS
    # ----------------------------------------------------------------------------

    def textOutput(self, output_file : Path, verbose: bool = False) -> None:
        self.verbose = verbose
        with open(output_file, "w") as txt:
            self.file_header(txt)
            self.CYAN_textOutput(txt)

    # ----------------------------------------------------------------------------
    #                               CYAN OUTPUTS
    # ----------------------------------------------------------------------------

    def file_header(self, txt):
        CMYK_ROOT = Path(__file__).resolve().parents[2]
        TOML_PATH = CMYK_ROOT / "pyproject.toml"

        if TOML_PATH.exists():
            with open(TOML_PATH, "rb") as f:
                toml_data = tomllib.load(f)
            self_version = toml_data.get("project", {}).get("version", "0.1.0")
        else: self_version = "0.1.0"

        now = datetime.now()
        model_file = Path(sys.argv[0]).name
        model_path = Path(sys.argv[0])
        config_file = self.Engine.cfg_path.name
        config_path = self.Engine.cfg_path
        user = getpass.getuser()

        timestamp_date = f"{now.strftime("DATE: %Y-%m-%d"):48s}"
        timestamp_time = f"{now.strftime("TIME: %H:%M:%S"):48s}"
        username    = f"USER:    {user:40s}"
        version_num = f"VERSION: {self_version:40s}"
        model_filename  = f"ENGINE MODEL FILE:  {model_file:24s} -> "
        config_filename = f"ENGINE CONFIG FILE: {config_file:24s} -> "

        txt.write(f"{timestamp_date}{username}\n"
                  f"{timestamp_time}{version_num}\n"
                  f"{model_filename}{model_path}\n"
                  f"{config_filename}{config_path}\n\n")

    def CYAN_textOutput(self, txt):
        self.CYAN_datalines(txt)
        self.CYAN_performance(txt)
        self.CYAN_config_report(txt)

    def CYAN_datalines(self, txt):
        # Set station name column widths
        station_number_width = 4    # Station number width modifier
        station_name_width = 12     # Station name width modifier

        # DEFINE VARIABLES OF INTEREST ================================================================
        # Variables will print out left-to-right in the same order as the out_vars list, regardless of verbosity

        out_vars = [
            OutVarCYAN('T0',        'K',       '',         False),
            OutVarCYAN('P0',        'Pa',      'kPa',      False),
            OutVarCYAN('h0',        'J/kg',    'kJ/kg',    False),
            OutVarCYAN('T',         'K',       '',         False),
            OutVarCYAN('P',         'Pa',      'kPa',      False),
            OutVarCYAN('h',         'J/kg',    'kJ/kg',    False),
            OutVarCYAN('s',         'J/kg/K',  'kJ/kg/K',  False),
            OutVarCYAN('M',         'NONDIM',  '',         False),
            OutVarCYAN('gamma0',    'NONDIM',  '',         False),
            OutVarCYAN('gamma',     'NONDIM',  '',         True),
            OutVarCYAN('gamma_avg', 'NONDIM',  '',         True),
            OutVarCYAN('Cp0',       'J/kg/K',  'kJ/kg/K',  False),
            OutVarCYAN('Cp',        'J/kg/K',  'kJ/kg/K',  True),
            OutVarCYAN('Cv0',       'J/kg/K',  'kJ/kg/K',  False),
            OutVarCYAN('Cv',        'J/kg/K',  'kJ/kg/K',  True),
            OutVarCYAN('FAR',       'kgf/kga', '',         False),
            OutVarCYAN('W',         'kg/s',    '',         False),
            OutVarCYAN('Wfactor',   'NONDIM',  '',         True),
            OutVarCYAN('Wstream',   'NONDIM',  '',         True),
        ]

        # GENERATE AND PRINT CYCLE DATA HEADER ==============================================================
        table_header = f"{"S##":>{station_number_width}s}{"STATION NAME":^{station_name_width*2+1}s}"
        for var in out_vars:
            if not var.verbose_only or self.verbose:
                table_header += var.header_segment
        table_header += "\n"

        txt.write(self.generateDivider(len(table_header), "CYCLE ANALYSIS"))
        txt.write(table_header)
        txt.write("=" * len(table_header) + "\n")

        # GENERATE AND PRINT LINE OF DATA ==================================================================
        dataline = ""
        for compName, compObj in self.Engine.flowpath.items():
            for flowName, flowObj in vars(compObj).items():
                if isinstance(flowObj, Flow):
                    dataline = f"{flowObj.name:>{station_number_width}s}{compName:>{station_name_width}s} {flowName:<{station_name_width}s}"

                    for var in out_vars:
                        if not var.verbose_only or self.verbose:
                            dataline += var.gen_dataline_segment(flowObj)
                    dataline += "\n"
                    txt.write(dataline)
            txt.write("-" * len(dataline) + "\n")

    def CYAN_config_report(self, txt):
        txt.write("\n")
        txt.write(self.standalone_block_header("PRESSURE RATIOS"))
        txt.write(OutVarCYAN('OPR',    'NONDIM', '', False, 'Overall Design Pressure Ratio').gen_standalone_dataline(self.Engine))
        for component in self.Engine.__dict__.values():
            if isinstance(component, Compressor):
                txt.write(OutVarCYAN('pr',     'NONDIM', '', False, f'{component.name} Design Pressure Ratio').gen_standalone_dataline(component))
        txt.write(self.standalone_block_header("MISC INFO"))
        txt.write(OutVarCYAN('bypass', 'NONDIM', '', False, 'Bypass Ratio').gen_standalone_dataline(self.Engine))
        for component in self.Engine.__dict__.values():
            if isinstance(component, Burner):
                txt.write(OutVarCYAN('FAR', 'NONDIM', '%', False, f'{component.name} Fuel-to-Air Ratio').gen_standalone_dataline(component))

        txt.write(self.standalone_block_header("COMPONENT EFFICIENCIES"))
        for component in self.Engine.__dict__.values():
            if isinstance(component, ComponentBase):
                if isinstance(component, Shaft):
                    txt.write(OutVarCYAN('eta_mech', 'NONDIM', '', False, F'{component.name:10s} (Mechanical)').gen_standalone_dataline(component))
                elif not (isinstance(component, Start) or isinstance(component, End)):
                    txt.write(OutVarCYAN('eta',      'NONDIM', '', False, f'{component.name:10s} (Isentropic)').gen_standalone_dataline(component))

    def CYAN_performance(self, txt):
        txt.write("\n")
        txt.write(self.standalone_block_header("THRUSTS"))
        txt.write(OutVarCYAN('total_thrust',  'N',      'lbf', False, 'Total Thrust').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('core_thrust',   'N',      'lbf', False, 'Core Thrust').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('bypass_thrust', 'N',      'lbf', False, 'Bypass Thrust').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('Fbypass_Fcore', 'NONDIM', '',    False, 'Bypass:Core Thrust Ratio').gen_standalone_dataline(self.Engine))
        txt.write(self.standalone_block_header("EFFICIENCIES"))
        txt.write(OutVarCYAN('thermal_eff',    'NONDIM', '%',      False, 'Thermal Efficiency').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('propulsive_eff', 'NONDIM', '%',      False, 'Propulsive Efficiency').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('total_eff',      'NONDIM', '%',      False, 'Total Efficiency').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('TSFC',           's/m', 'lb/lbf/hr', False, 'Thrust-Specific Fuel Consumption').gen_standalone_dataline(self.Engine))
        txt.write(self.standalone_block_header("MASS FLOW RATES"))
        txt.write(OutVarCYAN('Wtotal',  'kg/s', '', False, 'Total Mass Flow Rate').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('Wcore',   'kg/s', '', False, 'Core Mass Flow Rate').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('Wbypass', 'kg/s', '', False, 'Bypass Mass Flow Rate').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('Wfuel'  , 'kg/s', '', False, 'Fuel Mass Flow Rate').gen_standalone_dataline(self.Engine))
        txt.write(self.standalone_block_header("SPECIFIC THRUSTS"))
        txt.write(OutVarCYAN('specific_thrust_total',  'm/s', 'N*s/kg', False, 'Total Specific Thrust').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('specific_thrust_core',   'm/s', 'N*s/kg', False, 'Core Specific Thrust').gen_standalone_dataline(self.Engine))
        txt.write(OutVarCYAN('specific_thrust_bypass', 'm/s', 'N*s/kg', False, 'Bypass Specific Thrust').gen_standalone_dataline(self.Engine))
        txt.write(self.standalone_block_header("EXIT VELOCITIES"))
        for component in self.Engine.__dict__.values():
            if isinstance(component, End):
                txt.write(OutVarCYAN('u_out', 'm/s', '', False, f'{component.name} Exit Velocity').gen_standalone_dataline(component))
        txt.write(self.standalone_block_header("SPECIFIC REQUIRED POWER PER SHAFT"))
        for component in self.Engine.__dict__.values():
            if isinstance(component, Shaft):
                txt.write(OutVarCYAN('required_power', 'W', 'MW', False, f'{component.name} Required Power').gen_standalone_dataline(component))


class OutVarCYAN:
    """ OutVarCYAN objects are used to track variables of interest. They hold info about whether the value is to be printed only when verbose as well as the original_units and name of the variable. """
    data_width = 14
    data_precision = 3
    title_width = 32

    def __init__(self, name: str, original_units: str, display_units: str, verbose_only: bool, title: str = "") -> None:
        self.name = name
        self.title = title

        self.verbose_only = verbose_only
        self.original_units = original_units
        self.display_units = display_units
        self.convert = False

        dummy_float = 6.7

        if original_units == 'NONDIM':
            self.original_units = original_units = _NONDIM

        if original_units != _NONDIM:
            if display_units != '':
                try:
                    dummy_orig_units = Quantity(dummy_float, UR(original_units))
                except UndefinedUnitError:
                    raise RuntimeError("Original units are not defined.")
                try:
                    _ = dummy_orig_units.to(display_units).magnitude
                    header_title = self.name + ' (' + self.display_units + ')'
                    self.convert = True
                except UndefinedUnitError:
                    raise RuntimeError("Display units are not defined.")
                except DimensionalityError:
                    raise RuntimeError("Cannot convert between the two specified units.")
            else:
                header_title = self.name + ' (' + self.original_units + ')'
                self.display_units = original_units
        elif original_units != '':
            if display_units == '':
                header_title = self.name
            else:
                if display_units == '%':
                    header_title = self.name + ' (' + self.display_units + ')'
                    self.convert = True
                else:
                    raise RuntimeError("Cannot convert from nondim to non-percentage dimensional.")
        else:
            raise RuntimeError("Original units must be defined.")
        self.header_segment = f"{header_title:>{self.data_width}s}"

    def gen_dataline_segment(self, flow_obj) -> str:
        """Returns a formatted dataline segment, ready for addition into a dataline for printing."""
        if type(getattr(flow_obj, self.name)) is str:
            if not (self.original_units == _NONDIM and (self.display_units == '' or self.display_units == _NONDIM)):
                raise RuntimeError("User not allowed to specify units for a string data value.")
            dataline_segment = f"{getattr(flow_obj, self.name):>{self.data_width}s}"

        else:
            if self.convert:
                if getattr(flow_obj, self.name, None) is not None:
                    value_original_units = getattr(flow_obj, self.name) * UR(self.original_units)
                    value_display_units = value_original_units.to(self.display_units).magnitude
                    dataline_segment = f"{value_display_units:{self.data_width}.{self.data_precision}f}"
                else:
                    dataline_segment = "N/A"
            else:
                dataline_segment = f"{getattr(flow_obj, self.name):{self.data_width}.{self.data_precision}f}" \
                    if getattr(flow_obj, self.name, None) is not None else "N/A"

        return f"{dataline_segment:>{self.data_width}s}"

    def gen_standalone_dataline(self, flow_obj) -> str:
        formatted_title = f"{self.title:{self.title_width}s}" if self.title != "" else "NO TITLE: " + self.name
        data_segment = self.gen_dataline_segment(flow_obj)
        units = self.display_units
        return '\t' + formatted_title + data_segment + ' ' + units + '\n'
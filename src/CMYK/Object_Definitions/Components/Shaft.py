from CMYK.Object_Definitions.Base_Objects import ComponentBase

class Shaft(ComponentBase):

    def __init__(self, name):
        super().__init__(name, 'SHAFT')

        self.RPM = 0
        self.eta_mech = None
        self.generators = []    # List of power generators attached to the shaft i.e. turbines
        self.consumers = []     # List of power consumers attached to the shaft i.e. compressors, fans
        self.specific_required_power = None
        self.required_power = None

    def config(self) -> None:
        cfg = self.cfg[self.name]
        self.eta_mech = cfg['eta_mech']

    def calc_consumer_specific_required_power(self):
        self.specific_required_power = 0
        for consumer in self.consumers:
            consumer_flows = [_ for _ in consumer.__dict__.keys() if _[0:4] == 'Flow']
            num_flowouts = sum('FlowOut' in flow_name for flow_name in consumer_flows)
            num_flowins = sum('FlowIn' in flow_name for flow_name in consumer_flows)

            if num_flowins == 1 and num_flowouts == 1:
                self.specific_required_power += consumer.Wfactor * (consumer.FlowOut.h0 - consumer.FlowIn.h0)
            elif num_flowins > 1:
                raise RuntimeError(
                    "Shaft: Consumer has multiple FlowIn objects, unable to know which one to query for upstream conditions.")
            elif num_flowouts > 1:
                try:
                    self.specific_required_power += consumer.Wfactor * (consumer.FlowOut_COR.h0 - consumer.FlowIn.h0)
                except:
                    raise RuntimeError("Shaft: Consumer has multiple FlowOut objects without a 'FlowOut_COR' option.")
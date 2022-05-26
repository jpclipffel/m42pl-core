from textwrap import dedent


class Plan:
    """M42PL dispatcher and pipeline execution plan rendering.
    """

    class Step:
        """A step is a single command.
        """

        def __init__(self, text: str):
            self.text = text

        def render_plantuml(self) -> str:
            return f':{self.text};'

    class Layer:
        """A layer is a list of consecutive steps.
        """

        def __init__(self, name: str, kv: dict):
            self.name = name
            self.kv = kv
            self.steps = []

        def add_step(self, text: str):
            self.steps.append(Plan.Step(text))

        def render_plantuml(self) -> str:
            # Begin
            uml = dedent('''\
            partition "{name}" {{
              note
                Dispatcher
                ----
            ''').format(name=self.name)
            # Dispatcher KVs info
            for k, v in self.kv.items():
                uml += f'    {k}:{v}\n'
            uml += '  endnote\n\n'
            # Steps
            for step in self.steps:
                uml += f'  {step.render_plantuml()}'
                uml += '\n'
            # Close partition
            uml += '}\n'
            return uml

    def __init__(self):
        self.layers = []
    
    def add_layer(self, name: str, kv: dict = {}):
        self.layers.append(self.Layer(name, kv))
    
    def add_step(self, text: str, layer: int = -1):
        if len(self.layers) < 1:
            self.add_layer('0', {})
        self.layers[layer].add_step(text)
    
    def render_plantuml(self):
        uml = dedent('''\
        @startuml
        start

        ''')

        for layer in self.layers:
            uml += layer.render_plantuml()
            uml += '\n'

        uml += '@enduml'

        return uml

    def render(self, mode: str = 'plantuml'):
        """Render the whole plan.

        :param mode: Rendering language (e.g. PlantUML)
        """
        return getattr(self, f'render_{mode}')()

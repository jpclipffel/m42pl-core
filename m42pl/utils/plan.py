from textwrap import dedent, indent
from datetime import datetime


class Plan:
    """M42PL dispatcher and pipelines execution plan.
    """

    class Command:
        """Represents an MPL command.
        """

        def __init__(self, name: str):
            """
            :param name: Command's name
            """
            self.name = name

        def render_plantuml(self) -> str:
            return f':{self.name};'

    class Pipeline:
        """Represents an MPL pipeline, i.e. a list of commands.
        """

        def __init__(self, name: str):
            """
            :param name: Pipeline's name.
            """
            self.name = name
            self.start_time = self.stop_time = datetime.now()
            self.commands = []
        
        def add_command(self, name: str):
            """Adds a command to the pipeline.

            :param name: Command's name
            """
            self.commands.append(Plan.Command(name))
        
        def start(self):
            """Sets the pipeline start time.
            """
            self.start_time = datetime.now()
        
        def stop(self):
            """Sets the pipeline end time.
            """
            self.stop_time = datetime.now()

        @property
        def runtime(self):
            """Returns the pipeline's run-time.
            """
            return self.stop_time - self.start_time

        def render_plantuml(self) -> str:
            """Renders the pipeline as a PlantUML ``group``.
            """
            uml = dedent('''\
            group {name}
              note
                runtime: {runtime}
              endnote
            ''').format(name=self.name, runtime=self.runtime)
            # Commands
            for command in self.commands:
                uml += f'  {command.render_plantuml()}\n'
            # Close and return
            uml += 'end group'
            return uml

    class Layer:
        """Represents a set of parallels pipelines.
        """

        def __init__(self, name: str):
            """
            :param name: Layer's name
            """
            self.name = name
            self.start_time = self.stop_time = datetime.now()
            self.pipelines = []

        def add_pipeline(self, name: str):
            """Adds a pipeline to the layer.

            :param name: Pipeline's name.
            """
            self.pipelines.append(Plan.Pipeline(name))
        
        def add_command(self, name: str):
            """Adds a command to the latest pipeline in the layer.
            """
            if len(self.pipelines) < 1:
                self.add_pipeline('default')
            self.pipelines[-1].add_command(name)
        
        def start(self):
            """Sets the layer start time.
            """
            self.start_time = datetime.now()
        
        def stop(self):
            """Sets the layer stop time.
            """
            self.stop_time = datetime.now()
        
        @property
        def runtime(self):
            """Returns the layer run-time.
            """
            return self.stop_time - self.start_time

        def render_plantuml(self) -> str:
            """Renders the layer as a PlantUML ``partition``.
            """
            uml = dedent('''\
            partition "{name}" {{
              note
                runtime: {runtime}
              endnote
            ''').format(name=self.name, runtime=self.runtime)
            # Pipelines
            for i, pipeline in enumerate(self.pipelines):
                uml += f'  fork{i > 0 and " again" or ""}\n'
                uml += indent(pipeline.render_plantuml(), '    ')
                uml += '\n'
            uml += '  end fork\n'
            # Close and return
            uml += '}'
            return uml

    def __init__(self):
        self.layers = []
    
    def add_layer(self):
        """Adds a layer to the plan.
        """
        self.layers.append(self.Layer(name=f'L{len(self.layers)}'))
    
    def add_pipeline(self, name: str):
        """Adds a pipeline to the latest layer.

        :param name: Pipeline's name.
        """
        if len(self.layers) < 1:
            self.add_layer()
        self.layers[-1].add_pipeline(name)
    
    def add_command(self, name: str):
        """Adds a command to the latest pipeline in the latest layer.

        :param name: Command's name.
        """
        if len(self.layers) < 1:
            self.add_layer()
        self.layers[-1].add_command(name)
    
    def render_plantuml(self):
        """Renders the plan as a PlantUML source.
        """
        uml = dedent('''\
        @startuml
        start

        ''')
        # Layers
        for layer in self.layers:
            uml += layer.render_plantuml()
            uml += '\n'
        uml += '\n'
        # Close and return
        uml += '@enduml'
        return uml

    def render(self, mode: str = 'plantuml'):
        """Render the plan.

        :param mode: Rendering mode, i.e. PlantUML
        """
        return getattr(self, f'render_{mode}')()

"""Provides text processing routines."""

import copy
import time
from collections import deque

from .document import Document
from .processing_graphs import ProcessorNode
from lti_app.core.exceptions import TextProcessingException


class TextProcessor:
    """Implements a text processor using the graph pattern.

    Args:
        processing_graph (dict):
            The processing graph to use.
        graph_root (ProcessorNode):
            The graph root on which to start processing.
    """

    def __init__(self, processing_graph, graph_root):
        self.graph = copy.deepcopy(processing_graph)
        self.graph_root = graph_root

        if self.graph_root not in self.graph:
            raise TextProcessingException.invalid_graph()

    def __getitem__(self, key):
        if not isinstance(key, ProcessorNode):
            raise TypeError()

        if key not in self.graph:
            raise KeyError()

        return self.graph[key]

    def __setitem__(self, key, value):
        if not isinstance(key, ProcessorNode):
            raise TypeError()

        self.graph[key] = value

    def __contains__(self, item):
        return item in self.graph

    def __len__(self):
        return len(self.graph)

    def _process(self, document, processor, **kwargs):
        out_key = processor.attrs.get('out')

        if not isinstance(processor, ProcessorNode):
            raise TextProcessingException.invalid_processor_type(ProcessorNode)

        data = processor.process(
            document=document,
            **kwargs
        )
        document.put(out_key, data)

    def add_processor(self, node):
        if node in self.graph:
            return

        if not isinstance(node, ProcessorNode):
            raise TextProcessingException.invalid_processor_type(ProcessorNode)

        self.graph[node] = []

    def remove_processor(self, node):
        if node not in self.graph:
            return

        self.graph.pop(node, None)

        for source, targets in self.graph.items():
            self.graph[source] =\
                list(filter(lambda target: target != node, targets))

    def add_channel(self, source, target):
        if source not in self.graph or target not in self.graph:
            raise KeyError()

        if target in self.graph[source]:
            return

        self.graph[source].append(target)

    def run(self, text, **kwargs):
        """Run the processor.

        Args:
            text (str): The raw text to process.

        Returns:
            Document: The processed document.
        """

        document = Document(text)
        marked = []
        queue = deque()

        # Root processing
        self._process(document, self.graph_root, **kwargs)
        queue.append(self.graph_root)
        marked.append(self.graph_root)

        # Visit all reachable processors in the graph
        while len(queue) != 0:
            processor = queue.popleft()

            for next_processor in self.graph.get(processor):
                if next_processor not in marked:
                    start = time.clock()
                    self._process(
                        document,
                        next_processor,
                        input_key=processor.attrs.get('out'),
                        **kwargs
                    )
                    end = time.clock()
                    print('{} =====================> {}'.format(next_processor.attrs.get('name'), end - start))

                    marked.append(next_processor)
                    queue.append(next_processor)

        return document

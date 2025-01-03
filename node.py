from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class NodeEditor(QGraphicsView):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.temp_line = None  # Temporary line for connections
        self.start_connector = None  # Starting connector of the connection
        self.connections = []  # Store the connections between nodes

    def show_context_menu(self, position):
        context_menu = QMenu()

        add_node_action = context_menu.addAction("Add Node")
        add_node_action.triggered.connect(lambda: self.add_node(position))

        add_add_node_action = context_menu.addAction("Add 'Add' Node")
        add_add_node_action.triggered.connect(lambda: self.add_specific_node(position, "Add"))

        add_action_node_action = context_menu.addAction("Add 'Action' Node")
        add_action_node_action.triggered.connect(lambda: self.add_specific_node(position, "Action"))

        context_menu.exec_(self.mapToGlobal(position))

    def add_node(self, position):
        self.add_specific_node(position, "Default")

    def add_specific_node(self, position, node_type):
        scene_position = self.mapToScene(position)
        node = QGraphicsRectItem(0, 0, 120, 60)
        node.setPos(scene_position)
        node.setBrush(QBrush(Qt.lightGray))
        node.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.scene().addItem(node)

        text = QGraphicsTextItem(node_type, node)
        text.setDefaultTextColor(Qt.black)
        text.setPos(10, 10)

        # Add input connector
        input_connector = QGraphicsEllipseItem(-10, 20, 10, 10, node)
        input_connector.setBrush(QBrush(Qt.darkGray))
        input_connector.setPen(QPen(Qt.NoPen))
        input_connector.setData(0, "input")
        input_connector.setFlag(QGraphicsItem.ItemIsSelectable)

        # Add output connector
        output_connector = QGraphicsEllipseItem(120, 20, 10, 10, node)
        output_connector.setBrush(QBrush(Qt.darkGray))
        output_connector.setPen(QPen(Qt.NoPen))
        output_connector.setData(0, "output")
        output_connector.setFlag(QGraphicsItem.ItemIsSelectable)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsEllipseItem):  # Connector clicked
            connector_type = item.data(0)
            if connector_type == "output":  # Start a connection
                self.start_connector = item
                scene_pos = item.sceneBoundingRect().center()
                self.temp_line = QGraphicsLineItem(QLineF(scene_pos, scene_pos))
                self.temp_line.setPen(QPen(Qt.red, 2))
                self.scene().addItem(self.temp_line)
        super(NodeEditor, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_line:
            line = self.temp_line.line()
            line.setP2(self.mapToScene(event.pos()))
            self.temp_line.setLine(line)
        super(NodeEditor, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.temp_line:
            end_item = self.itemAt(event.pos())
            if isinstance(end_item, QGraphicsEllipseItem):
                end_type = end_item.data(0)
                if self.start_connector and end_type == "input" and self.start_connector.data(0) == "output":
                    # Complete the connection
                    start_pos = self.start_connector.sceneBoundingRect().center()
                    end_pos = end_item.sceneBoundingRect().center()

                    # Check if the connection already exists
                    if not self.is_connection_exists(self.start_connector, end_item):
                        connection_line = QGraphicsLineItem(QLineF(start_pos, end_pos))
                        connection_line.setPen(QPen(Qt.blue, 2))
                        self.scene().addItem(connection_line)
                        self.connections.append((self.start_connector, end_item, connection_line))
                    else:
                        print("Connection already exists.")
                else:
                    print("Invalid connection attempt.")
            else:
                print("Connection failed: Not a valid connector.")

            # Clean up temporary line
            self.scene().removeItem(self.temp_line)
            self.temp_line = None
            self.start_connector = None
        super(NodeEditor, self).mouseReleaseEvent(event)

    def is_connection_exists(self, start_connector, end_connector):
        """Check if the connection already exists between the start and end connectors."""
        for conn in self.connections:
            if conn[0] == start_connector and conn[1] == end_connector:
                return True
        return False

    def delete_connection(self, connection_line):
        """Remove a connection."""
        self.scene().removeItem(connection_line)
        self.connections = [conn for conn in self.connections if conn[2] != connection_line]

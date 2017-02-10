import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl


class EuclideanSensor(gl.GLViewWidget):
    def __init__(self):
        super().__init__()
        self.setCameraPosition(distance=40)
        self.add_grid()
        self.add_board()
        #self.add_sea()
        self.x = 0.
        self.y = 0.
        self.z = 0.

    def push_data(self, data):
        self.x, self.y, self.z = data

    def add_grid(self):
        self.grid = gl.GLGridItem()
        self.grid.scale(2, 2, 1)
        self.addItem(self.grid)

    def add_board(self):
        verts = np.array([
            [5, -3, 2], # front-right-top
            [5, 3, 2], # front-left-top
            [-5, -3, 2], # back-right-top
            [-5, 3, 2], # back-left-top
            [5, -3, -1], # front-right-bottom
            [5, 3, -1], # front-left-bottom
            [-5, -3, -1], # back-right-bottom
            [-5, 3, -1], # back-left-bottom
        ])
        faces = np.array([
            [0, 1, 2], # top
            [1, 2, 3], # top
            [4, 5, 6], # bottom
            [5, 6, 7], # bottom
            [0, 2, 4], # right
            [2, 4, 6], # right
            [1, 3, 5], # left
            [3, 5, 7], # left
            [0, 1, 4], # front
            [1, 4, 5], # front
            [2, 3, 6], # back
            [3, 6, 7], # back
        ])
        colors = np.array([
            [1, 1, 1, 1], # top
            [1, 1, 1, 1], # top
            [1, 1, 0, 1], # bottom
            [1, 1, 0, 1], # bottom
            [1, 0, 0, 1], # right
            [1, 0, 0, 1], # right
            [0, 1, 0, 1], # left
            [0, 1, 0, 1], # left
            [0, 0, 1, 1], # front
            [0, 0, 1, 1], # front
            [0, 1, 1, 1], # back
            [0, 1, 1, 1], # back
        ])

        self.board = gl.GLMeshItem(vertexes=verts, faces=faces,
                                  faceColors=colors, smooth=False,
                                  drawEdges=False)
        self.addItem(self.board)

        self.axis = gl.GLAxisItem()
        self.axis.setSize (x=10,y=10,z=10)
        self.addItem(self.axis)

    def add_sea(self):
        self.removeItem(self.grid)
        z = pg.gaussianFilter(np.random.normal(size=(100,100)), (1,1))
        self.sea = gl.GLSurfacePlotItem(z=z, shader='shaded',
                                        color=(0.5, 0.5, 1, 1),
                                        smooth=True)
        self.sea.translate(-50, -50, -1)
        self.addItem(self.sea)

    def update_view(self):
        self.board.resetTransform()
        self.board.rotate(self.x, x=1, y=0, z=0)
        self.board.rotate(self.y, x=0, y=1, z=0)
        self.board.rotate(self.z, x=0, y=0, z=1)

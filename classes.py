# this class is for the new workflow csv visualization
class CSVChunkInformation:
    filename = ''
    chunk_count = 0
    chunk_piece = []
    x_max_min = []
    y_max_min = []
    # This is used to mark which column should be visualized
    # 1 means visualize, 0 means not
    column_bool = []
    def __init__(self,filename,chunk_count,chunk_piece,x_max_min,y_max_min,column_bool):
        self.filename=filename
        self.chunk_count = chunk_count
        self.chunk_piece = chunk_piece
        self.x_max_min = x_max_min
        self.y_max_min = y_max_min
        self.column_bool = column_bool
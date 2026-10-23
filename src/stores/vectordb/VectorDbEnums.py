from enum import Enum  

class VectorDbEnums(Enum):
    QDRANT = "QDRANT"

class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"
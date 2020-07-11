import numpy as np
from collections import OrderedDict
from scipy.spatial import distance as dist

class CentroidTracker:
    def __init__(self, maxDisappeared=50, maxDistance=50):
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()

        self.maxDisappeared = maxDisappeared
        self.maxDistance = maxDistance

    def register(self, centroid):
        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):
        del self.objects[objectID]
        del self.disappeared[objectID]
        
    def clear(self):
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()

    def update(self, point):
        #point = [cx,cy,dx,dy,score,id]
        if len(point) == 0:
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
                    
            return self.objects

        inputCentroids = np.zeros((len(point), 6), dtype="float")
        
        for i, (cX, cY,dx,dy,score,Id) in enumerate(point):
            inputCentroids[i] = (cX, cY,dx,dy,score,Id)
#        print(inputCentroids)

        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i])

        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())
            
            D = dist.cdist(inputCentroids[:,0:2],np.array(objectCentroids)[:,0:2])
            
            same_obj = {}
            for n ,val in enumerate(D):
                ind = val.argmin()
                same_obj[n] = None
                # if val[ind]< (inputCentroids[n][2]//2):
                if val[ind]< self.maxDistance:
                    same_obj[n] = ind
                    
            for key in same_obj:
                if same_obj[key] is not None:
                    onb_active = objectIDs[same_obj[key]]
                    self.objects[onb_active] = inputCentroids[key]
                    self.disappeared[onb_active] = 0
                else:
                    self.register(inputCentroids[key])
                    
        return self.objects.copy()
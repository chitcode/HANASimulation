'''
# This is a simple simulation for inventory stock unit

# In this model there is only one supplier and one plant. Plant and supplier have mean and sigma deviation and also time deviations

Created on Nov 5, 2012

@author: chmohant
'''

from SimPy.Simulation import *
import ceODBC
import random
import sys


class Supplier(Process):
    
    def __init__(self,name,sim):
        Process.__init__(self,name=name,sim=sim)
        self.name = name
        self.r = random.Random(111) # seeding the random
        self.inventory = sim
        
    def supply(self,supplyQMu,supplyQSigma,supplyTMu=1,supplyTSigma=0):
        while True:
            quantiy = self.r.gauss(supplyQMu, supplyQSigma)
            time = self.r.gauss(supplyTMu, supplyTSigma)
            
            yield hold,self,time
            self.inventory.inventoryEntry(quantiy)
            
        
class Plant(Process):
    
    def __init__(self,name,sim):
        Process.__init__(self, name=name, sim=sim)
        self.name = name
        self.r = random.Random(222) # seeding the random
        self.inventory = sim
       
        
    def consume(self,consumeQMu,consumeQSigma,consumeTMu=1,consumeTSigma=0):
        while True:
            quantiy = self.r.gauss(consumeQMu, consumeQSigma)
            time = self.r.gauss(consumeTMu,consumeTSigma)
            
            yield hold,self,time
            self.inventory.inventoryEntry(-quantiy)
        

# Simulation class   
class InventorySim(Simulation):
    
    def __init__(self):
        Simulation.__init__(self)
        self.con = ceODBC.connect('DSN=SAPHANA;UID=BPANIGRA;PWD=Bimsap123')
        self.con.autocommit;       
        self.i = 0;
        
    def inventoryEntry(self,quantity):
        self.i +=1
        sql = "INSERT INTO BPANIGRA.INVENTORY_DEMO(SERIAL_ID,MATERIAL_ID,STORAGE_UNIT_ID,TIME,QUANTITY) VALUES("+str(self.i)+",1,1,"+str(round(self.now()))+","+str(round(quantity))+")"
        
        self.con.cursor().execute(sql)
        self.con.commit()
        #print(sql)
        
    def run(self,supplyQMu,supplyQSigma,supplyTMu,supplyTSigma,consumeQMu,consumeQSigma,consumeTMu,consumeTSigma):
        sup1 = Supplier("supplier1",self)
        plant1 = Plant("plant1",self)
        
        self.activate(sup1, sup1.supply(supplyQMu, supplyQSigma, supplyTMu, supplyTSigma))
        self.activate(plant1, plant1.consume(consumeQMu, consumeQSigma, consumeTMu, consumeTSigma))
                      
        self.simulate(maxRun)
        self.con.close()
        
#simulation parameters 
supplyQMu = 35       
supplyQSigma = 5
supplyTMu = 1
supplyTSigma = 0
consumeQMu = 500
consumeQSigma = 75
consumeTMu = 30
consumeTSigma = 10

maxRun = 1e6  # 1e6 for million use

inventory = InventorySim()
inventory.run(supplyQMu, supplyQSigma, supplyTMu, supplyTSigma, consumeQMu, consumeQSigma, consumeTMu, consumeTSigma)
    
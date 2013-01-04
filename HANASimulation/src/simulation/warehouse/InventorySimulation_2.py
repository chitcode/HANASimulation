'''
# This is a better simulation than the simple simulation ( InventorySimulation_1.py )for inventory stock unit

# In this model there are 2 supplier and one plant. Plant and supplier have mean and sigma deviation and also time deviations

Created on Nov 15, 2012

@author: chmohant
'''

from SimPy.Simulation import *
import ceODBC
import random
import sys
from msilib.schema import File


class Supplier(Process):
    
    def __init__(self,name,sim,seedVal):
        Process.__init__(self,name=name,sim=sim)
        self.name = name
        self.r = random.Random(seedVal) # seeding the random
        self.inventory = sim
        
    def supply(self,supplyQMu,supplyQSigma,supplyTMu=1,supplyTSigma=0):
        while True:          
            quantiy = round(self.r.gauss(supplyQMu, supplyQSigma))
            time = round(self.r.gauss(supplyTMu, supplyTSigma))
            if time > 0 and quantiy > 0: # as time and quantity should always be positive
                yield hold,self,time
                self.inventory.inventoryEntry("supplier",self.name,quantiy)
            
        
class Plant(Process):
    
    def __init__(self,name,sim):
        Process.__init__(self, name=name, sim=sim)
        self.name = name
        self.r = random.Random(222) # seeding the random
        self.inventory = sim
       
        
    def consume(self,consumeQMu,consumeQSigma,consumeTMu=1,consumeTSigma=0):
        while True:           
            quantiy = round(self.r.gauss(consumeQMu, consumeQSigma))
            time = round(self.r.gauss(consumeTMu,consumeTSigma))
            
            if time > 0 and  quantiy > 0: # as time and quantity should always be positive
                yield hold,self,time
                self.inventory.inventoryEntry("plant",self.name,-quantiy)
        

# Simulation class   
class InventorySim(Simulation):
    
    def __init__(self):
        Simulation.__init__(self)
        self.con = ceODBC.connect('DSN=SAPHANA;UID=BPANIGRA;PWD=Bimsap123')
        #cleaning the previous data
        self.con.cursor().execute("delete from BPANIGRA.INVENTORY_DEMO")
        self.con.commit()
        
        self.con.autocommit;       
        self.i = 0;
       
        
    def inventoryEntry(self,who,name,quantity):
        self.i +=1
        supplierName = ''
        plantName = ''
        if who == "plant":
            plantName = name
        if who == "supplier":
            supplierName = name
        values = str(self.i)+",1,1,'"+supplierName+"','"+plantName+"',"+str(self.now())+","+str(quantity)
        sql = "INSERT INTO BPANIGRA.INVENTORY_DEMO(SERIAL_ID,MATERIAL_ID,STORAGE_UNIT_ID,VENDOR,TARGET_PLANT,TIME,QUANTITY) VALUES("+values+")"
       
        self.con.cursor().execute(sql)
        self.con.commit()
        print(values)
        open("data_file.csv", mode='a').write(values)
        
    #def run(self,supplyQMu,supplyQSigma,supplyTMu,supplyTSigma,consumeQMu,consumeQSigma,consumeTMu,consumeTSigma):
    def run(self):
        sup1 = Supplier("SUPP1",self,111)
        sup2 = Supplier("SUPP2",self,666)
        sup3 = Supplier("SUPP3",self,888)
        plant1 = Plant("PLANT1",self)
        
        self.activate(sup1, sup1.supply(supply1QMu, supply1QSigma, supplyTMu, supplyTSigma))
        self.activate(sup2, sup2.supply(supply2QMu, supply2QSigma, supplyTMu, supplyTSigma))
        self.activate(sup3, sup3.supply(supply3QMu, supply3QSigma, supplyTMu, supplyTSigma))
        self.activate(plant1, plant1.consume(consumeQMu, consumeQSigma, consumeTMu, consumeTSigma))
        
        print("Simulation starts")              
        self.simulate(maxRun)        
        self.con.close()
        print("Simulation ends")
        
#simulation parameters 
supply1QMu = 35                 # mean quantity for supplier 1
supply1QSigma = 5               # deviation quantity for supplier 1
supply2QMu = 20                 # mean quantity for supplier 2
supply2QSigma = 2               # deviation quantity for supplier 2
supply3QMu = 12                # mean quantity for supplier 3
supply3QSigma = 1               # deviation quantity for supplier 3
supplyTMu = 4                   # Supplier mean time
supplyTSigma = 1                # supplier time deviation
consumeQMu = 500                # Plant/Consumer quantity mean
consumeQSigma = 75              # Plant/Consumer quantity deviation
consumeTMu = 30                 # Plant/Consumer time mean
consumeTSigma = 7             # Plant/Consumer time deviation

maxRun = 1000  # 1e6 for million use

inventory = InventorySim()
inventory.run()
    
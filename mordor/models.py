from django.db import models
from random import *

"""
@author: Alex Williams, Anthony Taormina, Daniel Whatley, Stephen Roca, Yuval Dekel
"""

# Create your models here.
class Party(models.Model):
    """
    Party
    """
    name = models.CharField(max_length=50)
    money = models.IntegerField(default = 5000)
    pace = models.FloatField(default = 1.) 
    rations = models.FloatField(default = 1.)
    location = models.IntegerField(default=0)
    stopmsg = models.CharField(max_length=1000, default="")
    
    def move(self):
        self.location += 1
        print "in move"
        print self.location
        print self.location
        return self.location

    def numAlive(self):
        """
        This function checks to see how many of the group members are still alive
        @return: The number of alive group members
        """
        return len(filter(lambda a: not a.checkIfDead(), self.character_set.all()))

    def kill(self):
        b = filter(lambda a: not a.isLeader, self.character_set.all())
        if b:
            q = b[__import__("random").randint(0,len(b)-1)]
            q.status = 0
            q.save()
            return q.name
        return ""

    def killall(self):
        for i in self.character_set.all():
            i.status = 0
            i.save()
            self.name += "--DEAD--"




    def consumeFood(self):
        """
        Attempts to consume a user determined amount of Food.
        @return: boolean: True upon a successful consumption and False upon a failure.
        """
        wag = Wagon.objects.get(id = self.id)
        ret = Inventory.objects.get(wagon = wag).removeItem("Food",self.rations*self.numAlive())
        if ret:
            wag.weight -= self.numAlive()*self.rations
            wag.save()
        return ret

    def __unicode__(self):
        """
        @return: String: String representation of a Party
        """
        return u'Party' + unicode(self.name)
    
class Character(models.Model):
    """
    Character
    """
    name = models.CharField(max_length=25, default="Character")
    profession = models.CharField(max_length=25, default = "")
    status = models.IntegerField(default = 1) 
    health = models.IntegerField(default = 1)
    isLeader = models.BooleanField(default = False)
    party = models.ForeignKey(Party)
    

    def __unicode__(self):
        """
        @return: String: String representation of a Character
        """
        return u'Char: '+ unicode(self.name)

    def checkIfDead(self):
        """
        Checks to see whether a player is dead or not
        @return: boolean: True if player is dead. False otherwise.
        """
        return self.status == 0
   
class Item(models.Model):
    name = models.CharField(max_length=25, default = "Garbage")
    description = models.CharField(max_length=500, default = "This item seems useless to your quest.")
    baseCost = models.IntegerField(default = 10)
    weight = models.IntegerField(default = 10)
    
    def __unicode__(self):
        """
        @return: String: String representation of a Item
        """
        return u'Baseitem:'+unicode(self.name)
    

class Store(models.Model):
    """
    Store
    """
    name = models.CharField(max_length=25, default = "General Store")
    items = models.ManyToManyField(Item)
    price_mult = models.FloatField(default = 1)
    location = models.IntegerField(default = -1)
    
    def __unicode__(self):
        """
        @return: String: String representation of a Store
        """
        return u'Store:'+ unicode(self.name)
    
    def hasItem(self, itemName):    #string
        """
        @param item: the item to check existence for
        Checks whether the store has the item at all
        @return: boolean: True if item exists in the Store false otherwise.
        """
        return Item.objects.get(name = itemName) in Store.objects.get(id=self.id).items_set.all()
 
class Wagon(models.Model):
    """
    Wagon
    """
    party = models.ForeignKey(Party)
    weight = models.FloatField(default = 0)
    capacity = models.IntegerField(default=500)
    
    def __unicode__(self):
        """
        @return: String: String representation of a Wagon
        """
        return u'Wagon:'+ unicode(self.party.name)
    
    def checkWagCap(self, base, amount): # item, int
        """
        @param item: the item to be added to the wagon 
        Checks to see if the added item exceeds the wagons capacity
        @return: boolean: True if adding the item does not exceed wagon capacity; false otherwise.
        """
        return not self.capacity < base.weight * amount + self.weight and base.weight*amount+self.weight>=0



class Inventory(models.Model):
    """
    Inventory
    """
    wagon = models.ForeignKey(Wagon)

    def __unicode__(self):
        """
        @return: String: the string representation of Inventory
        """
        par = self.wagon.party
        return u'Inventory:'+ unicode(par.name)
    
    def removeItem(self, iname, qty):
        if iname in map(lambda q: q.base.name, Inventory.objects.get(id=self.id).iteminstance_set.all()):
            iii=filter(lambda q: q.base.name==iname, Inventory.objects.get(id=self.id).iteminstance_set.all())[0]
            if iii.amount > qty:
                iii.amount -= qty
                iii.save()
                return True
            elif iii.amount == qty:
                iii.delete()
                return True
        return False

    def foodCount(self):
        if "Food" in map(lambda q: q.base.name, Inventory.objects.get(id=self.id).iteminstance_set.all()):
            iii=filter(lambda q: q.base.name=="Food", Inventory.objects.get(id=self.id).iteminstance_set.all())[0]
            return iii.amount
        else:
            return 0
    def itemCount(self, iname):
        if iname in map(lambda q: q.base.name, Inventory.objects.get(id=self.id).iteminstance_set.all()):
            iii=filter(lambda q: q.base.name==iname, Inventory.objects.get(id=self.id).iteminstance_set.all())[0]
            return iii.amount
        else:
            return 0 
    
class Iteminstance(models.Model):
    base = models.ForeignKey(Item)
    amount = models.IntegerField(default = 1)
    inventory = models.ForeignKey(Inventory)
    
    def __unicode__(self):
        """
        @return: String: String representation of a Iteminstance
        """
        return u'Iteminstance:'+unicode(Item.objects.get(id=self.base.id).name)
    
class Wagon(models.Model):
    """
    Wagon
    """
    party = models.ForeignKey(Party)
    weight = models.FloatField(default = 0)
    capacity = models.IntegerField(default=1000)
    
    def __unicode__(self):
        """
        @return: String: String representation of a Wagon
        """
        return u'Wagon:'+ unicode(self.party.name)
    
    def checkWagCap(self, base, amount): # item, int
        """
        @param item: the item to be added to the wagon 
        Checks to see if the added item exceeds the wagons capacity
        @return: boolean: True if adding the item does not exceed wagon capacity; false otherwise.
        """
        return not self.capacity < base.weight * amount + self.weight

class Event(models.Model):
    """
    Event
    """
    name = models.CharField(max_length=25)
    location = models.IntegerField(default = -1)
    etype = models.IntegerField(default = 0)
    #0 is river
    #1 is ...
    
    def __unicode__(self):
        """
        @return: String: String representation of a Event
        """
        return u'Event:' + self.name

    def text(self):
        return [
                "You arrived at a River, What will you do?"
                ][self.etype]

    def do(self):
        return 

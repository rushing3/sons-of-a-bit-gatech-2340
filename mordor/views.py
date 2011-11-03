from django.views.decorators.csrf import csrf_exempt
# Crjeate your views here.
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from mordor.models import Party, Character
from mordor.functions import * 
from mordor.coords import *



"""
@author: Alex Williams, Anthony Taormina, Daniel Whatley, Stephen Roca, Yuval Dekel
"""
@csrf_exempt
def start(request):
    return render_to_response("mordor/styletest.html", {})

@csrf_exempt
def init(request):
    populateLocations()
    return HttpResponse("Initialized!!!")

@csrf_exempt
def wag(request):
    alert, msg = 0, ""
    play = False
    try:
        request.GET['play']
        play = True
    except:
        pass
    party = Party.objects.get(id=request.GET['p'])
    w=party.wagon_set.all()[0]
    try:
        r = request.POST['river']
        if str(r)=="pay":
            alert = 1
            msg = takeFerry(request.GET['p'])
        elif str(r)=='caulk':
            rc = caulk()
            if rc!=0:
                alert = 1
                msg = rc
        else:
            rc = ford
            if rc!=0:
                alert = 1
                msg = rc
    except:
        pass

    try:
        party.pace = float(request.POST['pace'])
        party.rations = float(request.POST['ration'])
        party.save()
    except:
        pass
    if play:
        takeATurn(party.id)
    qq=0
    try:
        i = Wagon.objects.get(party=Party.objects.get(id=party.id))
        f = Item.objects.get(name="Food")
        qq=Iteminstance.objects.get(inventory=i.inventory,base=f).amount
    except:
        print "No"
        qq=0
    try:
        Store.objects.get(location=party.location)
        ts = True
    except:
        ts = False
    river = 0
    try:
        aa = Store.objects.get(location=party.location)
        alert = 1
        msg = "You have arrived at " + aa.name
    except:
        pass
    try:
        bb = Location.objects.get(index=party.location)
        river = 1
    except:
        pass
    if party.location>=130:
        alert = 1
        msg = "You are at the border of mordor... you take a single step forward and... ONE DOES NOT SIMPLY WALK INTO MORDOR!!!! you die of dyssentary"

    xx, yy = get_player_coords(party.location)
    xtop = (0 if xx<400 else (800 if xx>1200 else xx-400))
    ytop = (0 if yy<300 else (600 if yy>900 else yy-300))
    xx = 400 if 400<xx<1200 else (xx if xx<=400 else xx-800)
    yy = 300 if 300<yy<900 else (yy if yy<=300 else xx-900)

    return render_to_response("mordor/wag.html", {"partyid":request.GET['p'],"dt":party.location*6.25, "fpd":party.rations, "dpd":party.pace*12.5, 'rate2':party.pace, "fr":qq,"x":xx-24, "y":yy-20, "ytop":-ytop, "xtop":-xtop, 'testShop':ts, "alert":alert, 'msg':msg,"river":river})
@csrf_exempt
def inv(request):
    party = Party.objects.get(id=request.GET['p'])
    astore = party.wagon_set.all()[0].inventory
    items = map(lambda q: q.base, astore.iteminstance_set.all())
    return render_to_response("mordor/shoptest.html", {'partyid':request.GET['p'],"shopname":astore.name ,"items":items})


@csrf_exempt
def shop(request):
    party = Party.objects.get(id=request.GET['p'])
    print party.location
    try:
         astore= Store.objects.get(location=int(party.location-1))
    except:
         astore = Store.objects.get(location=0)
    items = astore.items.all()
    try:
        w=party.wagon_set.all()[0]
        print "wagon found!", request.POST['item'], request.POST['qty'], astore.price_mult
        buyItem(request.GET['p'],request.POST['item'],int( request.POST['qty']), astore.price_mult)
        print "receiving post for: " + request.POST['qty'], request.POST['item']
    except:
        print "couldn't find wagon or item"
    return render_to_response("mordor/shoptest.html", {'partyid':request.GET['p'],"shopname":astore.name ,"items":items, "party":party, 'weight':w.weight,"mult":astore.price_mult})

@csrf_exempt
def submit(request):
    try:
        if (request.POST['pp']):
            p = Party.objects.get(name=request.POST['pp'])
            p.delete()
    except:
        pass
    
    prof = request.POST['prof']
    mmult = {'r_holder':2,'gardener':1,'tmaker':.5}
    #create a new party
    partyz = Party(name=request.POST["p_name"], money=5000*mmult[prof], pace = float(request.POST['pace']),rations = float(request.POST['ration']))
    partyz.save()
    inv = Store(name="inventory", isVendor=False, price_mult=1)
    inv.save()
    w = Wagon(party=partyz, inventory=inv, weight=0)
    w.save()


    print w
    #create player
    pp = Character(name=request.POST['player'], profession=request.POST['prof'], status = 1, health = 1, isLeader = True, party = partyz)
    pp.save()
    #create members
    for q in ['m1','m2','m3']:
        if request.POST[q]:
            m= Character(name=request.POST[q], profession = "", status = 1, health = 1, isLeader = False, party = partyz)
            m.save()
    return HttpResponse("<p style='text-align:center;'>data received. visit <a href='../wagon.php?p="+str(partyz.id)+"'>the status page</a> to see your party.</p>")

@csrf_exempt
def config(request):
    p = Party.objects.get(id=request.GET['p'])

    return render_to_response("mordor/conf.html", {'testShop':True,'partyid':request.GET['p'],'part':p, "membs":p.character_set.all()})


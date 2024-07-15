from django.shortcuts import render, redirect
from datetime import datetime
from myapp.models import *
from django.db.models import Max
from django.http import HttpResponse

def HaveMsg(username):
    m1 = inviteToGroup.objects.filter(receiver = username).count()
    m2 = followRequest.objects.filter(receiver = username).count()
    m3 = inboxMsg.objects.filter(receiver = username, read = "False").count()
    if m1+m2+m3 != 0:
        haveMsg = "True"
    else:
        haveMsg = "False"
    return haveMsg

def main(request):
    return render(request, 'index.html', locals())

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        uName = request.POST.get('uName') # login.html 傳來的變數
        uPass = request.POST.get('uPass') # login.html 傳來的變數
        try: 
            user = student.objects.get(cName=uName, cPass = uPass)
            return redirect('../personal/'+uName)
        except:
            return render(request, 'login.html', {'msg': "Wrong sername or password."})
                   
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    elif request.method == 'POST':
        uName = request.POST.get('uName')
        uPass = request.POST.get('uPass')
        uGender = request.POST.get('uGender')
        uBirthday = request.POST.get('uBirthday')
        try:
            unit = student.objects.get(cName=uName)
            return render(request, 'signup.html', {'msg': "The username has been used. Please choose other name as username."})
        except:
            p = student(cName = uName, cPass = uPass, cSex = uGender, cBirthday = uBirthday)
            p.save()
            return redirect('/personal/'+uName)
            

def personalHome(request, username):
    unit = student.objects.get(cName=username)
    groups = group.objects.filter(member = username)
    groupsinfo = []
    for i in groups:
        count = group.objects.filter(groupid = i.groupid).count()
        groupsinfo.append({"groupid": i.groupid, "groupName": i.groupName, "isAdmin": i.isAdmin, "count": count})
    forums = forum.objects.filter(name=username)
    result = []
    for i in forums:
        replied = forumDiscuss.objects.filter(forumId = i.id).count()
        result.append({'title':i.title, "time": i.time, "count": replied, "id": i.id, "types": i.types})
    following = Following.objects.filter(name = username)
    fcount = following.count()
    followed = Following.objects.filter(following = username)
    fdcount = followed.count()

    haveMsg = HaveMsg(username)

    return render(request, 'personal.html', {'unit':unit, 'forums':result, "img": "/static/img/"+username+".png/", "fcount":fcount, "following":following, "fdcount":fdcount, "followed":followed, "groups": groupsinfo, "haveMsg": haveMsg})


def inbox(request, username):
    if request.method == 'GET':
        m=[]
        tmp = inviteToGroup.objects.filter(receiver = username)
        for i in tmp:
            g = group.objects.get(groupid=i.groupid, isAdmin = "True")
            m.append({'invitor':i.invitor, 'receiver': i.receiver, "groupid": i.groupid, "groupName": g.groupName})
        mcount = tmp.count()

        newfollowRequest = followRequest.objects.filter(receiver = username)
        fcount = newfollowRequest.count()

        newmsg = inboxMsg.objects.filter(receiver = username)
        if newmsg.count() > 0:
            for i in newmsg:
                i.read = "True"
                i.save()
        unit = student.objects.get(cName=username)
        return render(request, 'inbox.html', {"unit": unit, "newmsg":m, "followRequest":newfollowRequest, "img":"/static/img/"+username+".png/", "count": mcount+fcount, "inboxmsg": newmsg})
    
    elif request.method == 'POST':
        try:
            isaccepted = request.POST.get('accepted')
            groupid = request.POST.get('ID')
            maxid = group.objects.latest('id').id +1
            if isaccepted == "accepted":
                tmp = group.objects.get(groupid = groupid, isAdmin = "True")
                f = group(id = maxid, groupid = groupid, groupName = tmp.groupName, member = username, isAdmin="False")
                f.save()
            invitation = inviteToGroup.objects.get(receiver = username, groupid = groupid)
            invitation.delete()
        except:
            pass
        try:
            isallowed = request.POST.get('allowed')
            invitor = request.POST.get('follow')
            if isallowed == "accepted":
                f = Following(name = invitor, following = username)
                f.save()
            followrequest = followRequest.objects.get(receiver = username, invitor = invitor)
            followrequest.delete()
        except:
            pass
        try:
            deleteInbox = request.POST.get('deleteInbox')
            i = inboxMsg.objects.get(receiver = username, content = deleteInbox)
            i.delete()
        except:
            pass
        return redirect('/personal/' + username + '/inbox/')


def createForum(request, username):
    if request.method == 'GET':
        return render(request, 'createForum.html')
    elif request.method == 'POST':
        utitle = request.POST.get('title')
        ucontent = request.POST.get('content')
        try:
            uid = forum.objects.latest('id').id +1
        except:
            uid = 0 
        anonymous = request.POST.get('anonymous')
        if anonymous is None:
            anonymous = "False"
        elif anonymous is True:
            anonymous = "True"
        types = request.POST.get('types')
        f = forum(title = utitle, content = ucontent, name = username, time = datetime.now(), id = uid, anonymous = anonymous, types = types)
        f.save()

        follower = Following.objects.filter(following = username)
        if anonymous == "False":
            msgcontent = username + " posted a new forum \"" + utitle +"\""
            for i in follower:
                m = inboxMsg(receiver = i.name, content = msgcontent, link = "../forum/"+str(uid), time = datetime.now(), read="False")
                m.save()

        return redirect('/personal/'+username)

def editInfo(request, username):
    s = student.objects.get(cName=username)
    if request.method == 'GET':
        return render(request, 'editInfo.html', {'student':s, "birthday": str(s.cBirthday)})
    elif request.method == 'POST':
        s.cSex = request.POST.get('uGender')
        s.cBirthday = request.POST.get('uBirthday')
        s.introduction = request.POST.get('content')
        s.save()
        return redirect('/personal/'+username)
    
def deleteForum(request, username, forumId):
    replied = forumDiscuss.objects.filter(forumId = forumId)
    f = forum.objects.get(id = forumId)
    forum_link = "../forum/"+forumId 
    i = inboxMsg.objects.filter(link = forum_link)
    i.delete()
    f.delete()
    replied.delete()
    for i in replied:
        forumDiscussLike.objects.filter(forumDiscussId = i.id).delete()
    return redirect('/personal/'+username)

def likeComment(request, username, forumId, likeID):
    comment = forumDiscuss.objects.get(id = likeID)
    ifLiked = forumDiscussLike.objects.filter(forumDiscussId = likeID, likePerson = username)
    if ifLiked.count() != 0:
        ifLiked.delete()
        comment.like -= 1
    else:
        like = forumDiscussLike(forumDiscussId = likeID, likePerson = username)
        like.save()
        comment.like += 1
    comment.save()
    return redirect('/personal/'+username+'/forum/'+forumId)

def seeforum(request, username, forumId):
    if request.method == 'GET':
        f = forum.objects.get(id = forumId)
        haveMsg = HaveMsg(username)
        tmp_comment = forumDiscuss.objects.filter(forumId = forumId).order_by('time')
        comment = []
        for i in tmp_comment:
            isLiking = forumDiscussLike.objects.filter(forumDiscussId = i.id, likePerson = username).count()
            if isLiking != 0:
                comment.append({"id": i.id, "forumId": i.forumId, "name":i.name, "content":i.content, "time":i.time, "anonymous": i.anonymous, "like": i.like, "isLiking": True})
            else:
                comment.append({"id": i.id, "forumId": i.forumId, "name":i.name, "content":i.content, "time":i.time, "anonymous": i.anonymous, "like": i.like, "isLiking": False})
        return render(request, 'forum.html', {"forum":f, "comment": comment, "count":tmp_comment.count(), "username": username, "haveMsg": haveMsg})
        
    elif request.method == 'POST':
        content = request.POST.get('content')
        anonymous = request.POST.get('anonymous')
        if anonymous is None:
            anonymous = "False"
        elif anonymous is True:
            anonymous = "True"
        commentID = forumDiscuss.objects.latest('id').id +1
        c = forumDiscuss(id = commentID, name = username, forumId = forumId, time = datetime.now(), anonymous = anonymous, content = content, like = 0)
        c.save()
        writer = forum.objects.get(id = forumId)
        content = "There is a new comment in forum \"" + writer.title +"\""
        inboxMsg(receiver=writer.name, content = content, link = "../forum/"+str(forumId), time = datetime.now(), read=False).save()
        return redirect('/personal/'+username+'/forum/'+forumId)

def allforum(request, username):
    if request.method == "GET":
        haveMsg = HaveMsg(username)

        f = forum.objects.all()
        forums = []
        for i in f:
            replied = forumDiscuss.objects.filter(forumId = i.id).count()
            forums.append({"id": i.id, "title": i.title, "name": i.name, "content": i.content, "time":i.time, "count":replied, "anonymous": i.anonymous, "types": i.types, "haveMsg":haveMsg})
        return render(request, 'forums.html', {"forums":forums, "username": username, "haveMsg": haveMsg})
    
    elif request.method == "POST":
        search = request.POST.get('search')
        types = request.POST.get('types')
        if types != '--':
            f = forum.objects.filter(title__icontains = search, types = types)
        else:
            f = forum.objects.filter(title__icontains = search)
        forums = []
        for i in f:
            replied = forumDiscuss.objects.filter(forumId = i.id).count()
            forums.append({"id": i.id, "title": i.title, "name": i.name, "content": i.content, "time":i.time, "count":replied, "anonymous": i.anonymous, "types": i.types})
        return render(request, 'forums.html', {"forums":forums, "username": username})

def seeperson(request, username, name):
    if request.method == "GET":
        followrequest = "False"
        p = student.objects.get(cName = name)
        try:
            forums = []
            f = forum.objects.filter(name = p.cName, anonymous = "False")
            for i in f:
                replied = forumDiscuss.objects.filter(forumId = i.id).count()
                forums.append({"id": i.id, "title": i.title, "name": i.name, "content": i.content, "time":i.time, "count":replied})
        except:
            forums = None
        try:
            following = Following.objects.get(name = username, following = p.cName)
            following = "True"
        except:
            if name == username:
                following = "Self"
            else:
                following = "False"
                try:
                    followrequest = followRequest.objects.get(invitor = username, receiver = name)
                    followrequest = "True"
                except:
                    followrequest = "False"
        try:
            isfollowing = Following.objects.filter(name = p.cName)
        except:
            isfollowing = None
        haveMsg = HaveMsg(username)

        return render(request, 'seePerson.html', {"p": p, "username": username, "following": following, "followrequest": followrequest, "forums": forums, "isfollowing":isfollowing, "img": "/static/img/"+p.cName+".png/", "haveMsg":haveMsg})
    
    elif request.method == "POST":
        try:
            receiver = request.POST.get('follow')
            follow = followRequest(invitor = username, receiver = receiver)
            follow.save()
        except:
            isfollowing = request.POST.get('unfollow')
            follow = Following.objects.get(name = username, following = isfollowing)
            follow.delete()
        return redirect('/' + username + '/' + name + '/')
    
def deleteAccount(request, username):
    p = Following.objects.filter(name = username)
    p.delete()
    p = Following.objects.filter(following = username)
    p.delete()
    p = forumDiscuss.objects.filter(name = username)
    p.delete()
    p = forum.objects.filter(name = username)
    for i in p:
        tmp = forumDiscuss.objects.filter(forumId = i.id)
        tmp.delete()
        forum_link = "../forum/i.id"
        imsg = inboxMsg.objects.filter(link = forum_link)
        imsg.delete()
    p.delete()

    g = group.objects.filter(member = username)
    m = msg.objects.filter(sender = username)
    m.delete()
    for i in g:
        if i.isAdmin == "True":
            m=msg.objects.filter(groupId = i.groupid)
            m.delete()
            m=group.objects.filter(goupid = i.groupid)
            m.delete()
    g.delete()

    i = inviteToGroup.objects.filter(receiver = username)
    i.delete()
    i = inviteToGroup.objects.filter(invitor = username)
    i.delete()
    i = followRequest.objects.filter(receiver = username)
    i.delete()
    i = followRequest.objects.filter(invitor = username)
    i.delete()
    i = inboxMsg.objects.filter(receiver = username)
    i.delete()
    p = student.objects.filter(cName = username)
    p.delete()

    return redirect('/')

def createGroup(request, username):
    if request.method == 'GET':
        return render(request, 'createGroup.html')
    elif request.method == 'POST':
        groupName = request.POST.get('title')
        max = 0
        try:
            uid = group.objects.all()
            for i in uid:
                if i.groupid > max:
                    max = i.groupid
            max += 1
            tmp = group.objects.latest('id').id +1
        except: 
            tmp = 0
        f = group(id = tmp, groupid = max, groupName = groupName, member = username, isAdmin="True")
        f.save()
        return redirect('/personal/'+username)
    
def Group(request, username, groupid):
    if request.method == "GET":
        tmp = group.objects.filter(groupid = groupid)
        g = []
        m = []
        for i in tmp:
            g.append({"id": i.groupid, "groupName": i.groupName, "member": i.member, "memimg": "/static/img/"+i.member+".png/"})
        tmp1 = msg.objects.filter(groupId = groupid)
        for i in tmp1:
            m.append({"reply": i.reply, "content": i.content, "sender": i.sender, "time": i.time, "img": "/static/img/"+i.sender+".png/"})
        if group.objects.get(groupid = groupid, member = username).isAdmin == True:
            u = [{"username": username, "isAdmin": True}]
        else:
            u = [{"username": username, "isAdmin": False}]
        return render(request, 'groupchat.html', {"group":g, "msg": m, "user": u, "GroupName": tmp[0].groupName, "number": tmp.count()})
    
    elif request.method == "POST":
        m = request.POST.get('message')
        r = request.POST.get('replymsg')

        newmsg = msg(groupId = groupid, sender=username, time = datetime.now(), content = m, reply = r)
        newmsg.save()
        
        return redirect('/personal/'+username+'/Group/'+str(groupid))
        
def inviteGroupChat(request, username, groupid):
    following = Following.objects.filter(name = username)
    followed = Following.objects.filter(following = username)
    inviteFail = "False"
    haveMsg = HaveMsg(username)

    if request.method == "GET":
        return render(request, "inviteToGroup.html", {"following": following, "followed": followed, "haveMsg": haveMsg, "inviteFail": inviteFail})
    
    elif request.method == "POST":
        receiver = request.POST.get('inviteperson1')
        if receiver == None:
            receiver = request.POST.get('inviteperson2')

        tmp = inviteToGroup.objects.filter(receiver = receiver, groupid = groupid).count()
        tmp1 = group.objects.filter(member = receiver, groupid = groupid).count()

        if tmp+tmp1 == 0:
            m = inviteToGroup(groupid = groupid, invitor = username, receiver = receiver)
            m.save()
        elif tmp!=0:
            inviteFail = receiver + " has already been invited"
        elif tmp1!=0:
            inviteFail = receiver + " is in this group"

        return render(request, "inviteToGroup.html", {"following": following, "followed": followed, "haveMsg": haveMsg, "inviteFail": inviteFail})
        
def deleteGroup(request, username, groupid):
    g = group.objects.filter(groupid = groupid)
    g.delete()
    chat = msg.objects.filter(groupId = groupid)
    chat.delete()
    return redirect('/personal/'+username)

def leaveGroupChat(request, username, groupid):
    g = group.objects.get(groupid = groupid, member = username)
    if g.isAdmin == True:
        tmp = group.objects.filter(groupid = groupid, isAdmin = "False")
        if tmp.count == 0:
            deleteGroup(request, username, groupid)
        else:
            for i in tmp:
                i.isAdmin = "True"
                i.save()
    g.delete()
    return redirect('/personal/'+username)

def changeGroupName(request, username, groupid):
    if request.method == "GET":
        name = group.objects.get(groupid = groupid, isAdmin = "True")
        return render(request, 'changeGroupName.html', {"groupName": name.groupName})
    elif request.method == "POST":
        newname = request.POST.get('title')
        g = group.objects.filter(groupid = groupid)
        for i in g:
            i.groupName = newname
            i.save()
        return redirect('/personal/'+username)

def searchUser(request, username):
    haveMsg = HaveMsg(username)
    if request.method == "GET":
        return render(request, 'searchUser.html', {"username": username, "haveMsg": haveMsg})
    
    elif request.method == "POST":
        q = request.POST.get('search')
        p = student.objects.filter(cName__icontains = q)
        return render(request, 'searchUser.html', {"people": p, "count": p.count(), "username": username, "haveMsg": haveMsg})
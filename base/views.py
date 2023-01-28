from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from .models import Messages

from .forms import RoomForm, UserForm, MyUserCreationForm
from .models import Room, Topic, User

# Create your views here.


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exist')
        user = authenticate(
            request, username=username, password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(
                request, 'username or password invalid'
            )
    context = {
        'page': page
    }
    return render(
        request, 'base/login_register.html', context
    )


def logOutUser(request):
    logout(request)
    return redirect('home')
    # return redirect('login')

def _user_check(check_username):
    for i in User.objects.all():
        if str(i) == check_username:
            return True
        else:
            return False
            

def registerUser(request):
    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            password_1 =request.POST['password1']
            password_2 =request.POST['password2']
            username = request.POST['username']
            
            checking_user = _user_check(username)
            if checking_user:
                messages.error(request, "Username taken")
            if password_1 != password_2:
                messages.error(request, "Passwords aren't similar")
                
            messages.error(request, "zazu")
            
    context: dict[str, MyUserCreationForm] = {
        'form': form
    }
    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    """ you could use this instead if the one above
    if request.GET.get('q') != None:
        q = request.GET.get('q')
    else:
        q = ''"""
        
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)
    )
    room_messages = Messages.objects.filter(
        Q(room__topic__name__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()[0:5]
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages':room_messages
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.messages_set.all().order_by('created')
    pp = room.participants.all()
    if request.method == "POST":
        msg = Messages.objects.create(
            user=request.user,
            room=room,
            body=request.POST["body"],
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {
        "room": room,
        "room_messages": room_messages,
        'particpants': pp
    }
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.messages_set.all()
    topics = Topic.objects.all()
    context = {
        'user':user,
        'rooms':rooms,
        'room_messages':room_messages,
        'topics':topics
    }
    return render(
        request, 'base/profile.html', context
    )

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST['topic']
        topic, not_created = Topic.objects.get_or_create(name=topic_name)
        # TODO: add a conditional logic here to check for both name and cotnent of topic
        if not_created == True:
            Room.objects.create(
                host=request.user,
                topic=topic,
                name=request.POST['name'],
                description=request.POST['description']
            )
            return redirect('home')
    context = {
        'form': form,
        'topics':topics,
        'state':'create'
    }
    return render(request, 'base/create-room.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        from django.http import HttpResponse
        return HttpResponse("you're not allowed to update room")
    if request.method == 'POST':
        topic_name = request.POST['topic']
        topic, not_created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST['name']
        room.topic = topic
        room.description = request.POST['description'] 
        room.save()
        return redirect('home')
    context = {
        'form': form,
        'room':room,
        'state':'update'
    }
    return render(request, 'base/create-room.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {
        'obj': room
    }
    if request.user != room.host:
        return HttpResponse("you're not allowed to delete room")
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Messages.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("you're not allowed to delete message")
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {
        'obj': message
    }
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {
        'form':form
    }
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {
        'topics':topics
    }
    return render(
        request, 'base/topics.html', context
    )

def activityPage(request):
    room_messages = Messages.objects.all()
    context = {
        'room_messages':room_messages
    }
    return render(
        request, 'base/activity.html', context
    )
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from polls.models import Poll, Choice, Vote
from polls.forms import UserForm


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'


class ProfileView(generic.DetailView):
    model = User
    template_name = 'polls/profile.html'


# class VoteView(generic.ListView):
#     model = Poll


# def index(request):
#     latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
#     context = {'latest_poll_list': latest_poll_list}
#     return render(request, 'polls/index.html', context)


# def detail(request, poll_id):
#     poll = get_object_or_404(Poll, pk=poll_id)
#     return render(request, 'polls/detail.html', {'poll': poll})


# def results(request, poll_id):
#     poll = get_object_or_404(Poll, pk=poll_id)
#     return render(request, 'polls/results.html', {'poll': poll})


@login_required
def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {'poll': p, 'error_message': "You didn't select a choice"})
    else:
        if request.user.vote_set.filter(choice__poll=p).exists():
            return render(request, 'polls/detail.html', {'poll': p, 'error_message': "You have already voted on this poll"})
        else:
            v = Vote()
            v.choice = selected_choice
            v.user = request.user
            v.save()
            return redirect(reverse('polls:results', args=(p.id,)))


def user_login(request):
    context_dict = {}

    user = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('polls:index'))
            else:
                context_dict['disabled_account'] = True
                return render(request, 'polls/login.html', context_dict)
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            context_dict['bad_details'] = True
            return render(request, 'polls/login.html', context_dict)
    else:
        return render(request, 'polls/login.html', context_dict)


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('polls:index'))


def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
        else:
            print user_form.errors
    else:
        user_form = UserForm()

    context_dict = {'user_form': user_form}

    return render(request, 'polls/register.html', context_dict)

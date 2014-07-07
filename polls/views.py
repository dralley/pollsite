from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser
from polls.models import Poll, Choice, Vote
from polls.forms import UserForm, PollForm


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        return Poll.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class PollDetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'

    def get(self, request, pk, *args, **kwargs):
        p = get_object_or_404(Poll, pk=pk)

        if isinstance(request.user, AnonymousUser):
            return render(request, 'polls/detail.html', {'poll': p, 'error_message': "You are not logged in"})

        if request.user.vote_set.filter(choice__poll=p).exists():
            return redirect(reverse('polls:results', args=(p.id,)))

        return super(PollDetailView, self).get(request, pk, *args, **kwargs)


class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'

    def get(self, request, pk, *args, **kwargs):
        self.prev_choice = None
        p = get_object_or_404(Poll, pk=pk)
        self.vote_counts = {k.choice_text: k.vote_set.count() for k in p.choice_set.all()}

        if not isinstance(request.user, AnonymousUser):
            if request.user.vote_set.filter(choice__poll=p).exists():
                self.prev_choice = request.user.vote_set.filter(choice__poll=p)[0].choice

        return super(ResultsView, self).get(request, pk, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ResultsView, self).get_context_data(**kwargs)
        context.update({'prev_choice': self.prev_choice})
        context.update({'vote_counts': self.vote_counts})
        return context

class CreatePoll(generic.CreateView):
    model = Poll
    template_name = 'polls/create_poll.html'
    form_class = PollForm

    def get_initial(self):
        initial = super(CreatePoll, self).get_initial()
        author = self.request.user
        initial.update({
            'author': author,
            'pub_date': timezone.now()
        })
        return initial


def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    user = request.user

    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {'poll': p, 'error_message': "You didn't select a choice"})
    else:
        if not isinstance(user, AnonymousUser) and user.is_active:
            v = Vote()
            v.choice = selected_choice
            v.user = user
            v.save()
            return redirect(reverse('polls:results', args=(p.id,)))
        else:
            return render(request, 'polls/detail.html', {'poll': p, 'error_message': "You are not logged in"})


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
            user = authenticate(username=request.POST['username'], password=request.POST['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
            return redirect(reverse('polls:index'))
        else:
            print user_form.errors
    else:
        user_form = UserForm()

    context_dict = {'user_form': user_form}

    return render(request, 'polls/register.html', context_dict)

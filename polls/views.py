from django.shortcuts import render
from django.http import HttpResponse, get_object_or_404
from polls.models import Poll


def index(request):
    latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'polls/index.html', context)


def detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/detail.html', {'poll': poll})


def results(request, poll_id):
    return HttpResponse("You're looking at the results of poll %s" % poll_id)


def vote(request, poll_id):
    return HttpResponse("You're voting on poll %s" % poll_id)

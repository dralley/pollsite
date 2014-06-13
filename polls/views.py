from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from polls.models import Poll, Choice


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


# class VoteView(generic.ListView):
#     model = Poll


def index(request):
    latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'polls/index.html', context)


def detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/detail.html', {'poll': poll})


def results(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/results.html', {'poll': poll})


def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {'poll': p, 'error_message': "You didn't select a choice"})
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))


    # Request the context.
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {}
    context_dict['cat_list'] = cat_list
    # Boolean telling us whether registration was successful or not.
    # Initially False; presume it was a failure until proven otherwise!
    registered = False

    # If HTTP POST, we wish to process form data and create an account.
    if request.method == 'POST':
        # Grab raw form data - making use of both FormModels.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # Two valid forms?
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data. That one is easy.
            user = user_form.save()

            # Now a user account exists, we hash the password with the set_password() method.
            # Then we can update the account with .save().
            user.set_password(user.password)
            user.save()

            # Now we can sort out the UserProfile instance.
            # We'll be setting values for the instance ourselves, so commit=False prevents Django from saving the instance automatically.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Profile picture supplied? If so, we put it in the new UserProfile.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the model instance!
            profile.save()

            # We can say registration was successful.
            registered = True

        # Invalid form(s) - just print errors to the terminal.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render the two ModelForms to allow a user to input their data.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict['user_form'] = user_form
    context_dict['profile_form']= profile_form
    context_dict['registered'] = registered

    # Render and return!
    return render_to_response(
        'rango/register.html',
        context_dict,
        context)

# def user_login(request):
#     # Obtain our request's context.
#     context = RequestContext(request)
#     cat_list = get_category_list()
#     context_dict = {}
#     context_dict['cat_list'] = cat_list
#
#     # If HTTP POST, pull out form data and process it.
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#
#         # Attempt to log the user in with the supplied credentials.
#         # A User object is returned if correct - None if not.
#         user = authenticate(username=username, password=password)
#
#         # A valid user logged in?
#         if user is not None:
#             # Check if the account is active (can be used).
#             # If so, log the user in and redirect them to the homepage.
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect('/rango/')
#             # The account is inactive; tell by adding variable to the template context.
#             else:
#                 context_dict['disabled_account'] = True
#                 return render_to_response('rango/login.html', context_dict, context)
#         # Invalid login details supplied!
#         else:
#             print "Invalid login details: {0}, {1}".format(username, password)
#             context_dict['bad_details'] = True
#             return render_to_response('rango/login.html', context_dict, context)
#
#     # Not a HTTP POST - most likely a HTTP GET. In this case, we render the login form for the user.
#     else:
#         return render_to_response('rango/login.html', context_dict, context)
#
# @login_required
# def restricted(request):
#     context = RequestContext(request)
#     cat_list = get_category_list()
#     context_dict = {}
#     context_dict['cat_list'] = cat_list
#     return render_to_response('rango/restricted.html', context_dict, context)
#
# # Only allow logged in users to logout - add the @login_required decorator!
# @login_required
# def user_logout(request):
#     # As we can assume the user is logged in, we can just log them out.
#     logout(request)
#
#     # Take the user back to the homepage.
#     return HttpResponseRedirect('/rango/')
#

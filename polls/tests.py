import datetime
from django.test import TestCase
from django.utils import timezone
from polls.models import Poll, Choice, Vote
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import django_webtest

if User.objects.filter(username='dralley'):
    user = User.objects.get(username='dralley')
else:
    print 'creating new user'
    user = User(username='dralley')
    user.set_password('test')
    user.save()


def create_poll(question, days):
    """
    Creates a poll with the given 'question' published the given number of
    'days' offset to now (negative for polls published in the past, positive
    for polls that have yet to be published
    """
    return Poll.objects.create(author=user, question=question, pub_date=timezone.now() + datetime.timedelta(days=days))


# Create your tests here.
class PollMethodTests(TestCase):
    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_past_poll(self):
        """
        Tests that a past poll shows up in the list of polls on the index page
        """
        create_poll(question="Past poll.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Past poll.>'])

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently() should return False for polls whose pub_date
        is in the future
        """
        future_poll = create_poll('future_poll', 1)
        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        """
        was_published_recently() should return True for polls whose pub_date is
        within the last day
        """
        old_poll = create_poll('future_poll', -5)
        self.assertEqual(old_poll.was_published_recently(), False)

    def was_published_recently_with_recent_poll(self):
        """
        was_published_recently() should return True for polls whose pub_date is
        within the last day
        """
        recent_poll = Poll(pub_date=timezone.now() - datetime.timedelta(hours=1))
        self.assertEqual(recent_poll.was_published_recently(), True)


class PollViewsTests(django_webtest.WebTest):

    fixtures = ['polls_testdata.json']

    def test_index(self):
        """
        Tests that the index view returns 3 polls and that the polls are in the correct
        order, and have the correct choices
        """
        resp = self.client.get('/polls/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('latest_poll_list' in resp.context)
        self.assertEqual([poll.pk for poll in resp.context['latest_poll_list']], [3, 2, 1])
        poll_1 = resp.context['latest_poll_list'][0]
        self.assertEqual(poll_1.question, 'Which is the best Batman movie?')
        self.assertEqual(poll_1.choice_set.count(), 3)
        choices = poll_1.choice_set.all()
        self.assertEqual(choices[0].choice_text, 'Batman Begins')
        self.assertEqual(choices[1].choice_text, 'The Dark Knight')
        self.assertEqual(choices[2].choice_text, 'The Dark Knight Rises')

    def test_detail(self):
        """
        Tests that the detail view works correctly, returning 404 for a poll which does
        not exist and the correct question/choice data for one that does
        """
        resp = self.client.get('/polls/1/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['poll'].pk, 1)
        self.assertEqual(resp.context['poll'].question, 'What is the airspeed of an unladen swallow?')

        # Ensure that non-existent polls throw a 404.
        resp = self.client.get('/polls/4/')
        self.assertEqual(resp.status_code, 404)

    def test_results(self):
        """
        Tests that the results view returns the correct vote counts for poll id 1, and a
        404 for a poll that does not exist
        """
        resp = self.client.get('/polls/1/results/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['poll'].pk, 1)
        self.assertEqual(resp.context['poll'].question, 'What is the airspeed of an unladen swallow?')

        # Ensure that non-existent polls throw a 404.
        resp = self.client.get('/polls/4/results/')
        self.assertEqual(resp.status_code, 404)

    def test_good_vote(self):
        """
        Tests that a valid vote will redirect to the results page and increment the vote count on the selected choice
        """
        poll_1 = Poll.objects.get(pk=1)
        user = User.objects.get(username='test_user')
        self.assertEqual(poll_1.choice_set.get(pk=1).vote_set.count(), 0)

        form = self.app.get('/polls/1/vote/', user=user).form
        form['choice'] = 1
        resp = form.submit()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'], 'http://testserver/polls/1/results/')

        self.assertEqual(poll_1.choice_set.get(pk=1).vote_set.count(), 1)

    def test_logged_out_vote(self):
        """
        Tests that a vote while logged ou will refresh the page with an error message as expected
        """
        poll_1 = Poll.objects.get(pk=1)
        self.assertEqual(poll_1.choice_set.get(pk=1).vote_set.count(), 0)

        form = self.app.get('/polls/1/vote/').form
        form['choice'] = 1
        resp = form.submit()

        self.assertEqual(resp.status_code, 200)

    def test_create_new_poll(self):
        user = User.objects.get(username='test_user')

        form = self.app.get('/polls/new_poll/', user=user).form
        form['question'] = 'test_question'
        form['choice1'] = 'test_choice1'
        form['choice2'] = 'test_choice2'
        resp = form.submit()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'], 'http://testserver/polls/4/')

        new_poll = Poll.objects.get(pk=4)
        self.assertTrue(new_poll is not None)
        self.assertEqual(new_poll.question, 'test_question')

        choices = new_poll.choice_set.all()
        self.assertEqual(choices[0].choice_text, 'test_choice1')
        self.assertEqual(choices[1].choice_text, 'test_choice2')


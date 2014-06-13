import datetime
from django.test import TestCase
from django.utils import timezone
from polls.models import Poll
from django.core.urlresolvers import reverse

def create_poll(question, days):
    """
    Creates a poll with the given 'question' published the given number of
    'days' offset to now (negative for polls published in the past, positive
    for polls that have yet to be published
    """

# Create your tests here.
class PollMethodTests(TestCase):

    def test_index_view_with_no_polls(self):
        """
        If no polls exist, an appropriate message should be displayed
        """
        response =self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_poll_list'], [])

    def test_index_view_with_past_poll(self):
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_poll_list'], ['<Poll: Past poll.>'])

    def test_was_published_recently_with_future_poll(self):
        """
        was_published_recently() should return False for polls whose pub_date
        is in the future
        """
        future_poll = Poll(pub_date=timezone.now() + datetime.timedelta(days=30))
        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        """
        was_published_recently() should return True for polls whose pub_date is
        within the last day
        """
        old_poll = Poll(pub_date=timezone.now() - datetime.timedelta(days=5))
        self.assertEqual(old_poll.was_published_recently(), True)

    def was_published_recently_with_recent_poll(self):
        """
        was_published_recently() should return True for polls whose pub_date is
        within the last day
        """
        recent_poll = Poll(pub_date=timezone.now() - datetime.timedelta(hours=1))
        self.assertEqual(recent_poll.was_published_recently(), True)
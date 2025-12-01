from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Challenge(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_challenges')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def duration(self):
        """Return the duration of the challenge in days."""
        return (self.end_date - self.start_date).days

    def is_ongoing(self):
        """Check if the challenge is currently ongoing."""
        from django.utils import timezone
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def status(self):
        """Return the status of the challenge as one of: 'upcoming', 'active', 'done'.

        Logic:
        - If now is before start_date => 'upcoming'
        - If now is between start_date and end_date and `is_active` => 'active'
        - Otherwise => 'done' (either ended or administratively deactivated)
        """
        from django.utils import timezone
        now = timezone.now()
        if now < self.start_date:
            return 'upcoming'
        if self.start_date <= now <= self.end_date and self.is_active:
            return 'active'
        return 'done'


class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='scores')
    points = models.FloatField()
    date_scored = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'challenge')  # a user can submit only once per challenge

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} - {self.points} pts"

    # Methods for convenience
    def submit_score(self):
        self.save()

    @classmethod
    def get_user_score(cls, user_id):
        return cls.objects.filter(user_id=user_id)

    @classmethod
    def get_challenge_scores(cls, challenge_id):
        return cls.objects.filter(challenge_id=challenge_id)

    @classmethod
    def calculate_total_points(cls, user_id):
        from django.db.models import Sum
        return cls.objects.filter(user_id=user_id).aggregate(total_points=Sum('points'))['total_points'] or 0

    @classmethod
    def rank_users_by_points(cls):
        from django.db.models import Sum
        return cls.objects.values('user__username').annotate(total_points=Sum('points')).order_by('-total_points')


class Participant(models.Model):
    """Represents a user's participation in a challenge.

    This keeps track of who joined and when. Scores remain in the
    Score model so we can support multiple metrics if needed later.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"{self.user.username} in {self.challenge.title}"


# Convenience helpers on Challenge
def _challenge_get_leaderboard(self, top=5):
    """Return top `top` scores for this challenge as a list of dicts:
    [{'user': User, 'points': float}, ...]
    """
    from django.db.models import F
    qs = (Score.objects.filter(challenge=self)
          .select_related('user')
          .order_by('-points')[:top])
    return [{'user': s.user, 'points': s.points} for s in qs]


def _challenge_get_user_rank(self, user):
    """Return 1-based rank of `user` in this challenge or None if not ranked."""
    qs = (Score.objects.filter(challenge=self)
          .select_related('user')
          .order_by('-points'))
    rank = 1
    for s in qs:
        if s.user_id == getattr(user, 'id', None):
            return rank
        rank += 1
    return None


# Attach helper methods to Challenge dynamically to avoid touching class definition above
Challenge.get_leaderboard = _challenge_get_leaderboard
Challenge.get_user_rank = _challenge_get_user_rank


# Create your models here.

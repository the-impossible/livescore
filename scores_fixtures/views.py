from datetime import date
from itertools import chain
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (ListView, FormView, TemplateView,
                                   View, UpdateView, DeleteView)
from django.shortcuts import render, redirect

from . forms import FixturesForm
from . models import Fixture, Tournament, Team, Match, GoalScorers, Card, MatchStats, MatchAdditionalInfo
# Create your views here.

class HomeViewL(View):
    def get(self, request):
        context = {}
        current_date = date.today()
        fixture_date = Fixture.objects.filter(match_date_time__date=current_date)
        print(f"path: {request.path}")
        context['today_match'] = Match.objects.filter(fixture__in=fixture_date)
        context['next_match'] = Match.objects.filter(fixture__match_date_time__date__gt=current_date).first()

        context["rector_fixture"] = Fixture.objects.filter(tournament__name="rector_cup")
        context["dept_fixture"] = Fixture.objects.filter(tournament__name="departmental")
        context['ended'] = Match.objects.filter(status__in=['postponed', 'FT'])

        # match time
        try:
            match = Match.objects.get(fixture__match_date_time__date=current_date)
            context['match_time'] = match.time
        except Match.DoesNotExist:
            return render(request, "scores_fixtures/index.html", context=context)

        # print(f"id: {match.id}")

        if request.htmx:
            return render(request, "utils/match_card.html", context)
        else:
            return render(request, "scores_fixtures/index.html", context=context)


# def HomeViewL(request):
#     context = {}
#     current_date = datetime.date.today()
#     fixture_date = Fixture.objects.filter(match_date_time__date = current_date)
#     print(f"path: {request.path}")
#     context['today_match'] = Match.objects.filter(fixture__in=fixture_date)
#     context['next_match'] = Match.objects.filter(fixture__match_date_time__date__gt=current_date).first()

#     context["rector_fixture"] = Fixture.objects.filter(tournament__name = "rector_cup")
#     context["dept_fixture"] = Fixture.objects.filter(tournament__name = "departmental")
#     context['ended'] = Match.objects.filter(status__in = ['postponed', 'FT'])

#     # match time
#     match = Match.objects.get(fixture__match_date_time__date = current_date)
#     context['match_time'] = match.time

#     print(f"id: {match.id}")

#     if request.htmx:
#         return render(request, "utils/match_card.html", context)
#     else:
#         return render(request, "scores_fixtures/index.html", context=context)

# class HomeView(ListView):
#     model = Fixture
#     context_object_name = "matches"
#     template_name = "scores_fixtures/index.html"
#     # current_date = timezone.now().date()
#     current_date = datetime.date.today()
#     # print(f"current date: {current_date}")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         fixture_date = Fixture.objects.filter(match_date_time__date = self.current_date)

#         context['today_match'] = Match.objects.filter(fixture__in=fixture_date)
#         # context['home_team'] =
#         context["rector_fixture"] = Fixture.objects.filter(tournament__name = "rector_cup")
#         context["dept_fixture"] = Fixture.objects.filter(tournament__name = "departmental")
#         return context

# class UpdateMatchTime(UpdateView):
#     model =
class FixturesView(LoginRequiredMixin, SuccessMessageMixin, TemplateView, ListView, FormView):
    login_url = "auth:login"
    model = Fixture
    context_object_name = "rector"
    template_name = "scores_fixtures/rector_fixtures.html"
    object_list = Fixture.objects.all()
    success_message = "Fixtures Added"

    form_class = FixturesForm
    # success_url = reverse_lazy("auth:team_players", id)

    def get_template_names(self):
        template_name = self.kwargs.get('template_name')
        if template_name == 'rector-cup':
            return ["scores_fixtures/rector_fixtures.html"]
        elif template_name == 'departmental':
            return ["scores_fixtures/departmental_fixtures.html"]
        else:
            return ["utils/404.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # load form
        form = self.form_class()
        form.fields['tournament'].required = False
        template_name = self.kwargs['template_name']
        if template_name == "rector-cup":
            tournament = Tournament.objects.get(name="rector_cup")
            # print(f"tournament: {tournament}")
            form.fields['home_team'].queryset = Team.objects.filter(tournaments = tournament)
            form.fields['away_team'].queryset = Team.objects.filter(tournaments = tournament)
            # print("fixed")
        elif template_name == "departmental":
            tournament = Tournament.objects.get(name="departmental")
            form.fields['home_team'].queryset = Team.objects.filter(tournaments = tournament)
            form.fields['away_team'].queryset = Team.objects.filter(tournaments = tournament)

        # add to context based on the template_name
        if self.kwargs['template_name'] == "rector-cup":
            context["rector_fixture"] = Fixture.objects.filter(tournament__name = "rector_cup")
        elif self.kwargs['template_name'] == "departmental":
            context["dept_fixture"] = Fixture.objects.filter(tournament__name = "departmental")

        # add form and template_name to context
        context['form'] = form
        context['template_name'] = template_name
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form = self.form_class(request.POST)
        form.fields['tournament'].required = False
        template_name = self.kwargs['template_name']
        print(f"template: {template_name}")
        if template_name == "rector-cup":
            tournament = Tournament.objects.get(name="rector_cup")
            form.fields['home_team'].queryset = Team.objects.filter(tournaments = tournament)
            form.fields['away_team'].queryset = Team.objects.filter(tournaments = tournament)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.home_team = form.cleaned_data['home_team']
                instance.away_team = form.cleaned_data['away_team']
                instance.match_date_time = form.cleaned_data['match_date_time']

                if instance.home_team == instance.away_team:
                    messages.warning(request, "Both teams should be different")
                    return redirect("scores:fixtures", self.kwargs['template_name'])

                 # compare supplied date
                if instance.match_date_time.__lt__(timezone.now()):
                    messages.warning(request, "Older dates can't be supplied")
                    return redirect("scores:fixtures", self.kwargs['template_name'])

                # check if form already exist
                fixture = Fixture.objects.filter(match_date_time = instance.match_date_time).exists()
                if fixture:
                    messages.warning(request, "Fixture Present Already, Kindly check the form")
                    return redirect("scores:fixtures", self.kwargs['template_name'])


                instance.tournament = tournament
                instance.save()
                Match.objects.create(
                 fixture = instance
                )

                return redirect("scores:fixtures", self.kwargs['template_name'])
            else:
                messages.error(request, f"An error occurred: {form.errors.as_text}")
        elif template_name == "departmental":
            tournament = Tournament.objects.get(name="departmental")
            form.fields['home_team'].queryset = Team.objects.filter(tournaments = tournament)
            form.fields['away_team'].queryset = Team.objects.filter(tournaments = tournament)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.home_team = form.cleaned_data['home_team']
                instance.away_team = form.cleaned_data['away_team']
                instance.match_date_time = form.cleaned_data['match_date_time']

                if instance.home_team == instance.away_team:
                    messages.warning(request, "Both teams should be different")
                    return redirect("scores:fixtures", self.kwargs['template_name'])

                 # compare supplied date
                if instance.match_date_time.__lt__(timezone.now()):
                    messages.warning(request, "Older dates can't be supplied")
                    return redirect("scores:fixtures", self.kwargs['template_name'])

                instance.tournament = tournament
                instance.save()
                Match.objects.create(
                 fixture = instance
                )

                return redirect("scores:fixtures", self.kwargs['template_name'])
            else:
                messages.error(request, f"An error occurred: {form.errors.as_text}")
        else:
            messages.error(request, f"An error occured: {form.errors.as_text}")
            return redirect("scores:fixtures", self.kwargs['template_name'])

        return self.render_to_response(context)

class UpdateFixtureView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    login_url = "auth:login"
    model = Fixture
    template_name = "scores_fixtures/update_rector_fixture.html"
    form_class = FixturesForm
    success_message = "Fixtures Updated Successfully"

    def get(self, request, pk, *args, **kwargs):
        fixture_detail = self.model.objects.get(id = pk)
        form = self.form_class(instance = fixture_detail)

        template_name = self.kwargs['template_name']
        if template_name == "rector-cup":
            tournament = Tournament.objects.get(name="rector_cup")
            form.fields['home_team'].queryset = Team.objects.filter(tournaments = tournament)
            form.fields['away_team'].queryset = Team.objects.filter(tournaments = tournament)
            print("fixed")
        elif template_name == "departmental":
            tournament = Tournament.objects.get(name="departmental")
            form.fields['home_team'].queryset = Team.objects.filter(tournaments = tournament)
            form.fields['away_team'].queryset = Team.objects.filter(tournaments = tournament)

        # form.fields['home_team'].initial = Team.objects.get(deptName = fixture_detail.home_team.deptName)
        # form.fields['home_team'].queryset = Team.objects.filter(deptName = fixture_detail.home_team.deptName)
        return render(request, self.template_name, {"form":form})

    def post(self, request, pk, *args, **kwargs):
        fixture_detail = self.model.objects.get(id = pk)
        form = self.form_class(request.POST, instance = fixture_detail)
        form.fields['tournament'].required = False
        template_name = self.kwargs['template_name']

        if template_name == "rector-cup":
            tournament = Tournament.objects.get(name="rector_cup")
            form.fields['home_team'].queryset = Team.objects.filter(tournaments = tournament)
            form.fields['away_team'].queryset = Team.objects.filter(tournaments = tournament)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.home_team = form.cleaned_data['home_team']
                instance.away_team = form.cleaned_data['away_team']
                instance.match_date_time = form.cleaned_data['match_date_time']

                if instance.home_team == instance.away_team:
                    messages.warning(request, "Both teams can't be the same")
                    return redirect("scores:update_fixture", self.kwargs['template_name'], self.kwargs['pk'])

                 # compare supplied date
                if instance.match_date_time.__lt__(timezone.now()):
                    messages.warning(request, "Older dates can't be supplied")
                    return redirect("scores:update_fixture", self.kwargs['template_name'], self.kwargs['pk'])

                # check if the match has not been played
                match = Match.objects.get(fixture = self.kwargs['pk'])
                if match.status == 'FT':
                    messages.warning(request, "Fixture can't be updated because, it has been played.")
                    return redirect("scores:update_fixture", self.kwargs['template_name'], self.kwargs['pk'])

                instance.tournament = tournament
                instance.save()

                return redirect("scores:fixtures", self.kwargs['template_name'])
            else:
                messages.error(request, f"An error occurred: {form.errors.as_text}")
        elif template_name == "departmental":
            tournament = Tournament.objects.get(name="departmental")
            form.fields['home_team'].queryset = Team.objects.filter(tournaments = tournament)
            form.fields['away_team'].queryset = Team.objects.filter(tournaments = tournament)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.home_team = form.cleaned_data['home_team']
                instance.away_team = form.cleaned_data['away_team']
                instance.match_date_time = form.cleaned_data['match_date_time']

                if instance.home_team == instance.away_team:
                    messages.warning(request, "Both teams should be different")
                    return redirect("scores:fixtures", self.kwargs['template_name'])

                # compare date supplied
                if instance.match_date_time.__lt__(timezone.now()):
                    messages.warning(request, "Older dates can't be supplied")
                    return redirect("scores:fixtures", self.kwargs['template_name'])

                instance.tournament = tournament
                instance.save()

                return redirect("scores:fixtures", self.kwargs['template_name'])
            else:
                messages.error(request, f"An error occurred: {form.errors.as_text}")
        else:
            messages.error(request, f"An error occured: {form.errors.as_text}")
            return redirect("scores:fixtures", self.kwargs['template_name'])

        return render(request, self.template_name, {"form":form})

    def get_success_url(self):
        return reverse_lazy('scores:fixtures', kwargs={'template_name': self.request.POST['template_name']})

class DeleteFixtureView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = "auth:login"
    model = Fixture
    success_message = "Fixture Deleted Successfully"

    def get_success_url(self):
        return reverse_lazy('scores:fixtures', kwargs={'template_name': self.request.POST['template_name']})

class MatchesView(View):
    model = Match
    context_object_name = "matches"
    template_name = "scores_fixtures/rector_matches.html"
    object_list = Match.objects.all()

    def get_template_names(self):
        template_name = self.kwargs.get('template_name')
        if template_name == 'rector-cup':
            return ["scores_fixtures/rector_matches.html"]
        elif template_name == 'departmental':
            return ["scores_fixtures/departmental_matches.html"]
        else:
            return ["utils/404.html"]

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)

    #     template_name = self.kwargs['template_name']

    #     # add to context based on the template_name
    #     if template_name == "rector-cup":
    #         context["rector_matches"] = Match.objects.filter(fixture__tournament__name = "rector_cup", status__in = ['postponed', 'FT'])
    #     elif template_name == "departmental":
    #         context["dept_matches"] = Match.objects.filter(fixture__tournament__name = "departmental", status__in = ['postponed', 'FT'])

    #     context['template_name'] = template_name
    #     return context

    def get(self, request, *args, **kwargs):
        # context = self.get_context_data(**kwargs)
        context = {}
        template_name = self.kwargs['template_name']
        print(request.path)
        # add to context based on the template_name
        if template_name == "rector-cup":
            context["rector_matches"] = Match.objects.filter(fixture__tournament__name = "rector_cup", status__in = ['postponed', 'FT'])
        elif template_name == "departmental":
            context["dept_matches"] = Match.objects.filter(fixture__tournament__name = "departmental", status__in = ['postponed', 'FT'])
        return render(request, self.get_template_names(), context)
        # return self.render_to_response(context)

class MatchSummary(ListView):
    model = GoalScorers
    template_name = "scores_fixtures/match_summary.html"
    # context_object_name = 'match_summary'

    def get_queryset(self):
        match = Match.objects.get(pk=self.kwargs['pk'])
        match_summary = []
        goalScorers = GoalScorers.objects.filter(match = self.kwargs['pk']).order_by('time')
        cards = Card.objects.filter(match = match).order_by('time')
        additional_info = MatchAdditionalInfo.objects.filter(match=self.kwargs['pk']).order_by('time')

        print(f"{additional_info}")

        match_summary.append(goalScorers)
        match_summary.append(cards)
        match_summary.append(additional_info)

        merge_qs = list(chain(goalScorers, cards, additional_info))

        sorted_qs = sorted(merge_qs, key=lambda obj: obj.time)

        print(f"len-goalS: {len(goalScorers)}")
        print(f"len-card: {len(cards)}")
        print(f"len-merge_qs: {len(merge_qs)}")
        # print(f"merg_qs: {merge_qs}")

        for qs in sorted_qs:
            print(qs)

        return sorted_qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["match"] = Match.objects.get(pk=self.kwargs['pk'])
            # context['cards'] = Card.objects.filter(match = context['match']).order_by('time')
            context['match_stat'] = MatchStats.objects.filter(match = context['match'])
            # get cards count
            homeTeamRedCard = Card.objects.filter(match = context['match'], red_card__team_id = context['match'].fixture.home_team)
            awayTeamRedCard = Card.objects.filter(match = context['match'], red_card__team_id = context['match'].fixture.away_team)

            homeTeamYellowCard = Card.objects.filter(match = context['match'], yellow_card__team_id = context['match'].fixture.home_team)
            awayTeamYellowCard = Card.objects.filter(match = context['match'], yellow_card__team_id = context['match'].fixture.away_team)

            context['home_yellow'] = len(homeTeamYellowCard)
            context['away_yellow'] = len(awayTeamYellowCard)
            context['home_red'] = len(homeTeamRedCard)
            context['away_red'] = len(awayTeamRedCard)

            # print(f"context: {context}")


        except Match.DoesNotExist:
            return context
        return context






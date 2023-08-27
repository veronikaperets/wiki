from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from . import util
from django import forms
from django.contrib import messages
import random
import markdown2


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'content-textarea'}), label="Content")

class EditPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'content-textarea'}), label="Content")



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)

    # Convert the Markdown content to HTML
    html_content = markdown2.markdown(content)

    if content is None:
        return render(request, "encyclopedia/error.html", {
            "error_message": "The requested page was not found."
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content  # pass the HTML content instead of Markdown
    })


    

def search(request):
    query = request.GET.get('q')
    entries = util.list_entries()
    
    # If the query matches an entry exactly, redirect to that entry's page.
    if query in entries:
        return HttpResponseRedirect(reverse('encyclopedia:entry', args=[query]))
    
    # If the query is a substring of an entry, add that entry to the results list.
    results = [entry for entry in entries if query.lower() in entry.lower()]

    return render(request, 'encyclopedia/search.html', {
        'query': query,
        'results': results
    })


def create(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Check if the entry already exists
            if util.get_entry(title):
                messages.error(request, f"An entry with the title '{title}' already exists!")
                return render(request, "encyclopedia/create.html", {
                    "form": form
                })

            # Save the new entry and redirect to its page
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))

    return render(request, "encyclopedia/create.html", {
        "form": NewPageForm()
    })


def edit(request, title):
    entry_content = util.get_entry(title)

    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            new_content = form.cleaned_data["content"]
            util.save_entry(title, new_content)
            return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))
    else:
        form = EditPageForm(initial={'content': entry_content})

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form
    })


def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return HttpResponseRedirect(reverse("encyclopedia:entry", args=[random_entry]))
from turtle import title
from django.shortcuts import render, redirect, HttpResponseRedirect
from django import forms
from django.http import HttpRequest
from random import choice
from markdown2 import Markdown
import secrets

from . import util

markdowner = Markdown()

class SearchForm(forms.Form):
    search = forms.CharField(max_length=100)

class EditPageForm(forms.Form):
    # new_title = forms.CharField(label="Title:",max_length=100)
    # new_content = forms.CharField(widget=forms.Textarea(attrs={'name':'content','style':'height:40vh;width:70%;'}))
    old_title = forms.CharField(label="Title:",max_length=100)
    content = forms.CharField(widget=forms.Textarea(attrs={'name':'content','style':'height:40vh;width:70%;'}))


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title:",max_length=100)
    content = forms.CharField(widget=forms.Textarea(attrs={'name':'content','style':'height:40vh;width:70%;'}))

    
# HOME PAGE VIEW
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form" : SearchForm()
    })

# ENTRY PAGE VIEW
def entry_page(request, title):

    #  RETURN THE REQUESTED ENTRY IF IT EXISTS
    entry = util.get_entry(title)
    try:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdowner.convert(entry),
            "form" : SearchForm()
        })
    except TypeError:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": False,
            "form" : SearchForm()
        })


# SEARCH RESULTS VIEW
def search_results(request):
    # search = util.get_entry(search)
    
    results = []
    match = False

    if request.method == "GET":
        search = SearchForm(request.GET)  # A form bound to the POST data


        # check that the form is valid
        if search.is_valid():
            search = search.cleaned_data['search']
            search = str(search).casefold()
            
            entries = util.list_entries()
            # get the search request and compare to current entries
            for entry in entries:
                entry = entry.casefold()
                if search in entry:
                    results.append(entry)                   

                # RETURN ENTRY PAGE IF THE TITLE EXISTS
                if entry == search:
                    match = True
                    entry = markdowner.convert(util.get_entry(entry))
                    title = search.capitalize()

                    return render(request, "encyclopedia/entry.html", {
                        "title": title,
                        "content": entry,
                        "form" : SearchForm()
                    })
                
            # RENDER ERROR IF SEARCH DOESN'T MATCH ANY CURRENT ENTRIES
            return render(request, "encyclopedia/search_results.html", {
                "match" : match,
                "no_match" : "This search does not match or resemble any current entries.",
                "form" : SearchForm(),
                "entries": entries,
                "results" : results
            }) 


        # FORM IS INVALID
        else:

            return render(request, "encyclopedia/search_results.html", {
                            "Error" : "Please enter a valid search",
                            "form" : SearchForm()
                        }) 
    # RETURN INDEX IF GET REQUEST
    else:
        form = SearchForm()
        return index(request)
    
# ADD NEW ENTRY VIEW
def new_page(request):

    title_taken = False
    if request.method == "POST":

        entries = util.list_entries()
        add_page = NewPageForm(request.POST)

        if add_page.is_valid():
            new_title = str(add_page.cleaned_data['title'])
            new_content = add_page.cleaned_data['content']

            for entry in entries:
                if entry.casefold() == new_title.casefold():
                    title_taken = True
                    return render(request, "encyclopedia/new_page.html", {
                        'title_taken' : title_taken,
                        'new_page_form' : NewPageForm(),
                        'form' : SearchForm()
                    })
            
            # make the entry into a new page
            util.save_entry(new_title, new_content)
            return entry_page(request, new_title)

        # ENTRY IS NOT VALID
        else:
            return render(request, "encyclopedia/new_page.html", {
            'title_taken' : title_taken,
            'new_page_form' : NewPageForm(),
            'form' : SearchForm()
            })
    else:
        return render(request, "encyclopedia/new_page.html", {
            "new_page_form" : NewPageForm(),
            "form" : SearchForm()
        })

def edit_page(request, title):
    # IF GIVEN ENTRY DOESN'T EXIST
    error = False  
    if util.get_entry(title) == None:
        error = True
        return render(request, "encyclopedia/edit_page.html", {
            "error" : error,
            "form" : SearchForm(),
            "edit_page_form" : EditPageForm(),
            "entries" : util.list_entries()
        })
    entry = util.get_entry(title)
    if request.method == "POST":

    
    # ENTRY EXISTS. TAKE NEW ENTRY CONTENT AND REPLACE OLD ENTRY

        # GATHER INPUT VALUE AND SAVE ENTRY
        edit_form = EditPageForm(request.POST)
        # edit_form = edit_form({'new_content': })
        if edit_form.is_valid():
            # new_title = str(edit_form.cleaned_data['new_title'])
            new_content = edit_form.cleaned_data['content']

            util.save_entry(title, new_content)
            # RETURN UPDATED ENTRY PAGE
            return entry_page(request, title)
    # GET REQUEST AND TITLE IS VALID
    else:
        return render(request, "encyclopedia/edit_page.html", {
            "error" : error,
            "form" : SearchForm(),
            "edit_page_form" : EditPageForm({'old_title':title, 'content':entry}),
            "entries" : util.list_entries()
        })

def random(request):
    entries = util.list_entries()
    random_entry = secrets.choice(entries)
    if request.method == "POST":
        return entry_page(request, random_entry)
    else:
        return entry_page(request, random_entry)

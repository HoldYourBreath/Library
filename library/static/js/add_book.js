"use strict";

$( document ).ready(function() {
    $('#getBook').on('click', function (e) {
        fetch_book();
        return false;
    });

    $('#submitBook').on('click', function (e) {
        var tag = document.getElementById('tag').value;
        var isbn = document.getElementById('isbn').value;
        var title = document.getElementById('title').value;
        var author = document.getElementById('author').value;
        var description = document.getElementById('description').value;
        var thumbnail = document.getElementById('thumbnail').value;
        var pages = document.getElementById('num_pages').value;
        var pages = document.getElementById('num_pages').value;
        var publisher = document.getElementById('publisher').value;
        var publication_date = document.getElementById('publishedDate').value;
        var format = document.getElementById('format').value;
        // Validate inputs!
        var validationOk = true;
        var validationMessage = "Missing fields: ";
        if (!tag) {
            validationOk = false;
            validationMessage += " Tag"
        } else if (isNaN(parseInt(tag))) {
            validationOk = false;
            validationMessage = "Incorrect input format: Tag must be a integer."
        }
        if (!validationOk) {
            $("#error").html(validationMessage);
            $("#error").removeClass('hidden');
            return false;
        }

        var book = {
            isbn: isbn,
            title: title,
            pages: pages,
            publisher: publisher,
            format: format,
            publication_date: publication_date,
            authors: [author],
            description: description,
            thumbnail: thumbnail}

        $.ajax({
            url: '/api/books/' + tag,
            type: 'PUT',
            converters: 'text json',
            contentType: 'application/json',
            dataType: "json",
            error: function(err) {
                console.log(err);
            },
            data: JSON.stringify(book),
            success: function(resp) {
                console.log(resp);
            }
        });
    })

    $('#isbn').on('keypress', function(e) {
        var code = e.keyCode || e.which;
        if(code==13){
            fetch_book();
        }
    });
});

function setErrorMessage(msg) {
    $("#error").html(msg);
    $("#error").removeClass('hidden');
}

function clearErrorMessage() {
    $("#error").addClass('hidden');
}

function fetch_book() {
    var isbn = document.getElementById('isbn').value;
    $.get( '/api/books/goodreads/' + isbn, function( response ) {
        document.getElementById('title').value = response.title;
        document.getElementById('author').value = response.author[0];
        document.getElementById('description').value = response.description;
        document.getElementById('thumbnail').value = response.thumbnail;
        document.getElementById('num_pages').value = response.num_pages;
        document.getElementById('format').value = response.format;
        var publication_date = response.publication_date.replace(/ /g, "-");
        $('#publishedDate').val(publication_date);
        $('#publisher').val(response.publisher);
    });
    return false;
}
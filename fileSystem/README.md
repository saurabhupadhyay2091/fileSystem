<p>Some basic requirements that I have ignored to focus on the business logic more:</p>
<ol>
<li>I have not use .env file for credentials ( its hard- coded)</li>
<li>I have not included proper logging.</li>
<li>I have not handled the exceptions</li>
</ol>
<p>sync_file_system.py : this file helps the user to create folders and upload folders wherever the user likes.
app.py: Its uses celery and rabbitMQ to handle upload and download asynchronously</p>
<p>I HAVE NOT IMPLEMENTED THE SEARCH FILE FUNCTIONALITY DUE TO TIME CONSTRAINT</p>
<p>Suggestion: In future ,Either readymade environment should be give OR additiona time should be given to the candidates to first set up their local environment before proceeding ahead with the assignment, as it becomes challenging to when something gets stuck and the candidate has to spend time ( even if those skills are not being checked.)</p>

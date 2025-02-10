Falcon
================

This is a heavily customizable Python package serving as a wrapper and a pipeline for parsing 
mathematical problems to LLMs. 

Modes of work
--------------------------
Falcon supports two modes: synchronous (sync) and asynchronous (async). In sync execution one 
calls the model in real-time and receives the solutions or answers as the return result of the 
called function. In async mode one parses the tasks to the model and receives an ID that later be 
used to retrieve the result when they are ready.

Pipelines
--------------------------
For extended support Falcon allow the user to create their own abstract pipelines to communicate 
with different LLMs (via API or locally). To create a new pipeline one must create a ``.py`` file in 
the ``pipelines`` folder following the ``pipe_template.py``. Three method must be implemented: one for 
sync communication (``retrieve_response``), one to send a batch for async execution (``send_batch``) 
and one for retrieving the result of the async job (``retrieve_batch``). Implementation details can be 
found in the template file. Once the new is created, one must modify the ``pipes_list.py`` file add the 
name and the filename of the new pipeline.

Challenger: Initialize
---------------------------
Once the pipelines are setup, one can move forward to actually sending problems to the model. For this, 
the ``Challenger(pipename='OpenAI', model=None, Template=None, temperature=None, max_tokens=None)`` class is provided. In inialization you may choose the 
pipeline you wish to use and choose a template. One can also specify a template that may look like this:

    Please solve the following problem: {statement};

or like this:

    Please solve the following problem: {statement}; Here is a hint that might help: {hint};

In the first case you cannot parse problem-specific hints later, while in the second - you can. Here is an example 
initialization:

    from falcon import Challenger

    solver = Challenger()
    solver.set_pipe("OpenAI")
    solver.set_model("o3-mini")
    solver.set_temperature(1)

There are two pre-implemented pipelines: for OpenAI (pipename is ``OpenAI``) and for TogetherAI (pipename is ``Together``).
Note: If you are using your own prompting template and want to parse hints you must include a ``{hint}`` handle in it. Otherwise if you haven't 
specified a template the package will take care of it. To avoid confusition please do not ask the model to format the answer in a specific way 
as this is already included in the script.

Challenger: Sync jobs
-------------------------
Sync tasks can be executed via the ``solve_problems(problems, hints=None, output_type='solutions', voters=1, vote=True)`` 
method. The ``problems`` arguments must be a list of string being the problem statements. The ``hints`` can be a list of 
string each being a hint for solving its corresponding problem. If left as ``None`` hints are not passed. The ``output_type`` 
must be either ``solutions`` (retrieving the complete solutions to each problems) or ``answers`` (extracting only the answer to 
the problem). The argument ``voters`` specifies how many times the problem must the parsed to the model. If ``vote`` is set to 
``True`` the output of the method is a list of strings, each being the answers to each corresponding problems. In this case the 
answer is chosen as the must voted answers among the voters. If ``vote`` is set to ``False`` then the output is a list of lists, 
each containing all received answers from the voters for each correspoding problem. Example:

    problems = ["What is the greated prime number smaller than 100?", "How much is 8 times 7?", "What is the sum of all positive 
    integers smaller that 100?"]

    answers = solver.solve_problems(problems, output_type='answers', voter=5, vote=True)

Challenger: Async jobs
---------------------------
Async tasks can be send to the model using the ``send_problems(problems, hints=None, voters=1)`` method. Here the arguments serve the 
same purpose as the corresponding arguments in the sync method.

    problems = ["What is the greated prime number smaller than 100?", "How much is 8 times 7?", "What is the sum of all positive 
    integers smaller that 100?"]
    hints = ["The number 89 is prime.", "", "Start by summing the first and the last number"]

    id = solver.send_problems(problems, hints=hints, voters=10)

Here ``id`` is a string can be later used to retrieve the result by the ``retrieve_problems(batch_id, output_type='solutions', vote=True)`` 
method where the arguments have the same meaning as in the sync job method. Example:

    answers = solver.retrieve_problems(id, output_type='answers', vote=False)
    
Grading and evaluation
----------------------------
For grading and evaluation of the models the static methods ``grade(answers, answers_ground_truth)`` and ``grade_solution(solutions, answers_ground_truth)`` 
are provided. They work in the same way except for the fact that the second extracts the answers from the solutions (that must be received from a 
Challenger). The ``answers`` (and ``solutions``) must a list. Each item can be either an answers (solution) or a list of answers (solutions). The output for
both method is a list of floats represiting the fraction of answers (solutions) that were correct.

    answers_correct = ["97", "56", "4950"]
    evalution = Challenger.grade(answers, answers_correct)

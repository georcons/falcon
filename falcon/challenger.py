from .pipelines import Pipeline
from .scheduler import Scheduler

DEFAULT_TEMPLATE = "Please solve the following problem: {statement};"
DEFAULT_HINT_TEMPLATE = "Please solve the following problem: {statement}; Here is a hint that might help: {hint};"

class Challenger:
    def __init__(self, pipename='OpenAI', model=None, template=None, temperature=None, max_tokens=None):
        self.set_pipe(pipename)
        self.set_template(template)
        self.set_model(model)
        self.set_temperature(temperature)
        self.set_max_tokens(max_tokens)
        self.concurrent_requests = 1
        self.max_retries = 1
        self.delay = 0.1
        self.gpus = False

    def gpu_setup(self, gpu_type, gpu_count):
        self.gpus = True
        self.gpu_type = gpu_type
        self.gpu_count = gpu_count

    def set_pipe(self, pipename):
        if pipename in Pipeline.get_pipes():
            self.pipeline = Pipeline(pipename)
            self.pipename = pipename
        else:
            raise Exception("Invalid pipe name - '" + pipe_name + "'")

    def set_model(self, model):
        if model == None:
            self.model = self.pipeline.DEF_MODEL
        else:
            self.model = model

    def set_temperature(self, temperature):
        if temperature == None:
            self.temperature = self.pipeline.DEF_TEMPERATURE
        else:
            self.temperature = temperature
        
    def set_max_tokens(self, max_tokens):
        self.max_tokens = max_tokens

    def get_max_tokens(self):
        return self.max_tokens 

    def get_temperature(self):
        return self.temperature

    def get_model(self):
        return self.model

    def get_pipe(self):
        return self.pipename

    # Example Template
    # Hello. Please solve the following problem: {statement}.
    # Here is a hint that may help you: {hint}.
    # It MUST include {statement}.
    # It MAY include {hint}
    def set_template(self, template):
        self.default_template = template == None
        if self.default_template:
            self.template = DEFAULT_TEMPLATE
        elif template.find('{statement}') == -1:
            raise Exception("Template must have a {statement} attribute.")
        else:
            self.template = template

    def compile_problems(self, statements, hints=None):
        local_template = self.template.strip()
        if hints != None:
            if len(statements) != len(hints):
                raise Exception("Number of problems and number of hints must the same")
            if local_template.find("{hint}") == -1:
                if self.default_template:
                    local_template = DEFAULT_HINT_TEMPLATE
                else:
                    raise Exception("To parse hints your problem template must include a {hint} attribute")

        output = []
        index = 0

        for statement in statements:
            prompt = "Please reason step by step, and put your final answer within \\boxed{} at the end of the solution. "
            prompt += local_template.replace("{statement}", statement.strip())
            if hints != None:
                prompt = prompt.replace("{hint}", hints[index].strip())
                index += 1
            output.append(prompt)
        
        return output

    @staticmethod
    def extract_answers(solutions):
        answers = []
        for solution in solutions:
            ind_start = solution.rfind("boxed{") + len("boxed{")
            ind_end = solution.find("}", ind_start)
            if ind_start == -1 or ind_end == -1:
                answers.append(None)
            else:
                ans = solution[ind_start:ind_end:]
                answers.append(ans)
        return answers

    def solve_problems(self, problems, hints=None, output_type='solutions', voters=1, vote=True):
        if hints != None and len(problems) != len(hints):
            raise Exception("Number of problems and number of hints must the same")
        if output_type != 'solutions' and output_type != 'answers':
            raise Exception("Output type be either 'solutions' or 'answers'")
        prompts = self.compile_problems(problems, hints)
        total_count = len(prompts)
        current_count = 0
        s = Scheduler(self.pipeline.retrieve_response)
        kwargs = {
            "model": self.model,
            "temperature": self.temperature,
            "response_count": voters
        }
        model_output = s.run(prompts, **kwargs)
        results = []
        for res in model_output:
            # res = self.pipeline.retrieve_response(prompt, model=self.model, temperature=self.temperature, response_count=voters)
            if vote:
                solution = self._do_voting(res, output_type=output_type)
                results.append(solution)
            else: 
                if output_type == 'solutions':
                    results.append(res)
                else:
                    results.append(self.extract_answers(res))
            
            current_count += 1
        return results

    def _do_voting(self, solutions, output_type='solutions'):
        candidates = {}
        answers = self.extract_answers(solutions)
        index = 0
        for answer in answers:
            if answer in candidates:
                candidates[answer]["count"] += 1
            else:
                candidates[answer] = {"count": 1, "index": index}
            index += 1
        max_key = None
        max_votes = 0
        for candidate in candidates:
            if candidates[candidate]["count"] > max_votes:
                max_key = candidate
                max_votes = candidates[candidate]["count"]
        return solutions[candidates[max_key]['index']] if output_type == 'solutions' else max_key

    def send_problems(self, problems, hints=None, voters=1):
        if hints != None and len(problems) != len(hints):
            raise Exception("Number of problems and number of hints must the same")
        prompts = self.compile_problems(problems, hints)
        if self.gpus:
            return self.pipeline.send_batch(
                prompts, 
                model=self.model, 
                temperature=self.temperature, 
                response_count=voters,
                gpu_type=self.gpu_type,
                gpu_count=self.gpu_count
            )
        return self.pipeline.send_batch(prompts, model=self.model, temperature=self.temperature, response_count=voters)

    def retrieve_problems(self, batch_id, output_type='solutions', vote=True):
        if output_type != 'solutions' and output_type != 'answers':
            raise Exception("Output type must be either 'solutions' or 'answers'")
        results = self.pipeline.retrieve_batch(batch_id)

        if results == None:
            return None
        
        output = []


        if vote:
            for res in results:
                solution = self._do_voting(res, output_type=output_type)
                output.append(solution)
        
        else:
            if output_type == 'solutions':
                output = results
            else:
                for problem in results:
                    output.append(self.extract_answers(problem))

        return output
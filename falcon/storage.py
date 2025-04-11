from typing import List
from datetime import datetime
from datasets import load_dataset, Dataset

_RESERVED_ID_COLUMN = "__id"

_STATEMENT_DS_SUFFIX = "_statements"
_STATEMENT_COLUMN = "statement"
_STATEMENT_KEYS = [_RESERVED_ID_COLUMN, _STATEMENT_COLUMN, "type", "answer", "domain", "custom_id", "solution"]

_EXPERIMENT_DS_SUFFIX = "_experiments"
_EXPERIMENT_KEYS = [_RESERVED_ID_COLUMN, "name", "description", "model"]

_RESULTS_DS_SUFFIX = "_results"
_RESULTS_KEYS = [_RESERVED_ID_COLUMN, "experiment_id", "problem_id", "prompt", "model_solution", "date"]

class Storage:
    def __init__(
        self,
        statements,
        experiments,
        results
    ):
        # Validate keys in statements
        for key in _STATEMENT_KEYS:
            if key not in statements:
                raise Exception(f"There must be a {key} key in statements.")
        for key in statements:
            if key not in _STATEMENT_KEYS:
                raise Exception(f"Invalid key {key} in statements.")
        
        # Validate keys in experiments
        for key in _EXPERIMENT_KEYS:
            if key not in experiments:
                raise Exception(f"There must be a {key} key in experiments.")
        for key in experiments:
            if key not in _EXPERIMENT_KEYS:
                raise Exception(f"Invalid key {key} in experiments.")

        # Validate keys in results
        for key in _RESULTS_KEYS:
            if key not in results:
                raise Exception(f"There must be a {key} key in results.")
        for key in results:
            if key not in _RESULTS_KEYS:
                raise Exception(f"Invalid key {key} in results.")

        # Retrieve table lengths
        self.__statements_count = len(statements[_RESERVED_ID_COLUMN])
        self.__experiments_count = len(experiments[_RESERVED_ID_COLUMN])
        self.__results_count = len(results[_RESERVED_ID_COLUMN])

        # Validate column lengths
        for key in _STATEMENT_KEYS:
            if len(statements[key]) != self.__statements_count:
                raise Exception(f"Dismatch in column lengths of statements (check {key})")
        
        for key in _EXPERIMENT_KEYS:
            if len(experiments[key]) != self.__experiments_count:
                raise Exception(f"Dismatch in column lengths of experiments (check {key})")

        for key in _RESULTS_KEYS:
            if len(results[key]) != self.__results_count:
                raise Exception(f"Dismatch in column length of results (check {key})")

        # Write local variables
        self.__statements = statements
        self.__experiments = experiments
        self.__results = results

    @staticmethod
    def create(
        name : str,
        description : str | None = ""
    ):
        statements = {key: [] for key in _STATEMENT_KEYS}
        experiments = {key: [] for key in _EXPERIMENT_KEYS}
        results = {key: [] for key in _RESULTS_KEYS}
        proj = Storage(statements, experiments, results)
        proj.name = name
        proj.description = description
        return proj

    def add_problems(
        self,
        statements : List[str],
        **kwargs
    ) -> None:
        # Check for duplicates
        for statement in statements:
            if statement in self.__statements[_STATEMENT_COLUMN]:
                raise Exception(f"Problem '{statement}' is already in the storage.")

        # Get number of statements to add
        count = len(statements)
        
        # Validate inputs arguments
        for key in kwargs:
            if key == _RESERVED_ID_COLUMN:
                raise Exception(f"Column '{_RESERVED_ID_COLUMN}' is reserved.")
            if key == _STATEMENT_COLUMN:
                raise Exception(f"Column '{_STATEMENT_COLUMN}' is reserved.")
            if key not in _STATEMENT_KEYS:
                raise Exception(f"Invalid argument {key}.")
            if not isinstance(kwargs[key], list):
                raise Exception(f"Argument {key} must a list.")
            if len(kwargs[key]) != count:
                raise Exception(f"Column {key} is of invalid length.")

        # Initalize __id column
        ids = list(range(self.__statements_count, self.__statements_count + count))

        # Add problems
        for key in _STATEMENT_KEYS:
            if key == _RESERVED_ID_COLUMN:
                self.__statements[_RESERVED_ID_COLUMN] += ids
            elif key == _STATEMENT_COLUMN:
                self.__statements[_STATEMENT_COLUMN] += statements
            elif key in kwargs:
                self.__statements[key] += kwargs[key]
            else:
                self.__statements[key] += [None for _ in range(count)]

        # Increment count
        self.__statements_count += count

    def create_experiment(
        self,
        name : str,
        description : str | None = "",
        *,
        model : str | None = ""
    ) -> int:
        # Check if name is free
        if name in self.__experiments:
            raise Exception("Experiment with that name already exists.")
        # Add experiment
        self.__experiments[_RESERVED_ID_COLUMN].append(self.__experiments_count)
        self.__experiments["name"].append(name)
        self.__experiments["description"].append(description)
        self.__experiments["model"].append(model)
        # Increment experiment count
        self.__experiments_count += 1
        # Return current ID
        return (self.__experiments_count - 1)

    def __get_experiment_by_name(
        self,
        name : str
    ) -> int:
        if not name in self.__experiments["name"]:
            return None
        else:
            index = self.__experiments["name"].index(name)
            return {key: self.__experiments[key][index] for key in _EXPERIMENT_KEYS}

    def __get_problem_by_id(
        self,
        _id : int
    ):
        if _id not in self.__statements[_RESERVED_ID_COLUMN]:
            raise Exception(f"Identification number {_id} not in STATEMENT table.")
        else:
            index = self.__statements[_RESERVED_ID_COLUMN].index(_id)
            return {key: self.__statements[key][index] for key in _STATEMENT_KEYS}

    def add_results(
        self,
        experiment : str,
        model_solutions : List[List[str] | str],
        *,
        prompts : List[str] | None = None,
        statements : List[str] | None = None
    ) -> None:
        # Make sure experiment is valid
        eid = self.__get_experiment_by_name(experiment)[_RESERVED_ID_COLUMN]
        if eid == None:
            eid = self.create_experiment(experiment)

        count = len(model_solutions)

        # Augment prompts if not parsed
        prompts = prompts if prompts != None else [None for _ in range(count)]

        # Validate lengths  
        if len(prompts) != count:
            raise Exception("Number of prompts must be the same as the number of results.")
        if statements != None and len(statements) != count:
            raise Exception("Number of statements muust be the smae as the number of results.")

        # Retrieve statement ids
        statement_ids = [-1 for _ in range(count)]
        if statements == None:
            if count > len(self.__statements[_RESERVED_ID_COLUMN]):
                raise Exception("Not enought statements imported.")
            statement_ids = [self.__statements[_RESERVED_ID_COLUMN][k] for k in range(count)]
        
        else:
            for i, statement in enumerate(statements):
                if statement not in self.__statements[_STATEMENT_COLUMN]:
                    raise Exception(f"Statement {statement} not found in STATEMENT table. Make sure to add it.")
                statement_ids[i] = self.__statements[_STATEMENT_COLUMN].index(statement)

        # Generate ids
        ids = list(range(self.__results_count, self.__results_count + count))

        # Flatten the model_solution lists and generate column augmentations
        aug_problem_ids = []
        aug_prompts = []
        aug_model_solutions = []
        total_count = 0

        for i, entry in enumerate(model_solutions):
            if isinstance(entry, str):
                entry = [entry]
            aug_model_solutions += entry
            local_count = len(entry)
            aug_problem_ids += [statement_ids[i] for _ in range(local_count)]
            aug_prompts += [prompts[i] for _ in range(local_count)]
            total_count += local_count
        
        aug_ids = list(range(self.__results_count, self.__results_count + total_count))
        aug_experiment_ids = [eid for _ in range(total_count)]
        cdate = datetime.now().isoformat()
        aug_dates = [cdate for _ in range(total_count)]

        # Augment Columns
        self.__results[_RESERVED_ID_COLUMN] += aug_ids
        self.__results["experiment_id"] += aug_experiment_ids
        self.__results["problem_id"] += aug_problem_ids
        self.__results["prompt"] += aug_prompts
        self.__results["model_solution"] += aug_model_solutions
        self.__results["date"] += aug_dates

        # Increment count
        self.__results_count += total_count

    def add_result(
        self,
        experiment : str,
        model_solution : str,
        *,
        prompt : str | None = None,
        statement : str | None = None
    ) -> None:
        self.add_results(
            experiment, 
            [[model_solution]], 
            prompts=(None if prompt == None else [prompt]),
            statements=(None if statement == None else [statement])    
        )
    
    def experiments(self):
        return self.__experiments['name']

    def problems(self):
        return self.__statements[_STATEMENT_COLUMN]

    def get_experiment(
        self,
        name : str
    ):
        # Fetch experiment
        experiment = self.__get_experiment_by_name(name)
        if experiment == None:
            raise Exception(f"Invalid experiment name: {name}.")
        eid = experiment[_RESERVED_ID_COLUMN]

        # Initialize problems temp dictionary
        problems_temp = {}

        # _RESULTS_KEYS = [_RESERVED_ID_COLUMN, "experiment_id", "problem_id", "prompt", "model_solution", "date"]

        # Add problems and generations
        for i, entry_eid in enumerate(self.__results["experiment_id"]):
            # If problem not added already, add it
            if entry_eid == eid:
                prob_id = self.__results["problem_id"][i]
                if prob_id not in problems_temp:
                    problems_temp[prob_id] = self.__get_problem_by_id(prob_id)
                    problems_temp[prob_id]["generations"] = []

                # Add this generation
                problems_temp[prob_id]["generations"].append({
                    "user": self.__results["prompt"][i],
                    "assistant": self.__results["model_solution"][i],
                    "date": self.__results["date"][i]
                })
        
        # Convert the dictionary to list
        problems_lst = [problems_temp[key] for key in list(problems_temp.keys())]

        # Add to output
        experiment["problems"] = problems_lst

        # Return output
        return experiment

    def get_experiment_lists(
        self,
        name : str
    ):
        experiment = self.get_experiment(name)
        problems = experiment['problems']
        number_problems = len(problems)
        statements = [None for _ in range(number_problems)]
        answers = [None for _ in range(number_problems)]
        results = [[] for _ in range(number_problems)]
        for i, problem in enumerate(problems):
            statements[i] = problem['statement']
            answers[i] = problem['answer']
            for gen in problem['generations']:
                results[i].append(gen['assistant'])
        return statements,answers,results

    def dev_print(self):
        print(self.__statements, "\n")
        print(self.__experiments, "\n")
        print(self.__results, "\n")

    @staticmethod
    def load_project(
        path : str, 
        *,
        token : str | None = None
    ):
        statements = load_dataset(path + _STATEMENT_DS_SUFFIX, token=token)['train'].to_dict()
        experiments = load_dataset(path + _EXPERIMENT_DS_SUFFIX, token=token)['train'].to_dict()
        results = load_dataset(path + _RESULTS_DS_SUFFIX, token=token)['train'].to_dict()
        return Storage(statements, experiments, results)

    def push_to_hub(
        self,
        path : str,
        *,
        token : str | None = None
    ):
        ds_statements = Dataset.from_dict(self.__statements)
        ds_experiments = Dataset.from_dict(self.__experiments)
        ds_results = Dataset.from_dict(self.__results)
        ds_statements.push_to_hub(path + _STATEMENT_DS_SUFFIX, token=token)
        ds_experiments.push_to_hub(path + _EXPERIMENT_DS_SUFFIX, token=token)
        ds_results.push_to_hub(path + _RESULTS_DS_SUFFIX, token=token)
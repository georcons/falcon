from .challenger import Challenger

class Grader:
    @staticmethod
    def grade(answers_list, answers_ground_truth):
        if len(answers_list) != len(answers_ground_truth):
            raise Exception("Number of answers lists must the same as the number of answers in the ground truth list.")

        output = []
        index = 0
        for answers in answers_list:
            if not isinstance(answers, list):
                if isinstance(answers, str):
                    answers = [answers]
                else:
                    raise Exception("Each item in answers_list must be a list of answers.")
            total_count = len(answers)
            count = 0
            for ans in answers:
                if ans == str(answers_ground_truth[index]):
                    count += 1
            output.append(count / total_count)
            index += 1

        return output

    @staticmethod
    def grade_solutions(solutions_list, answers_ground_truth):
        if len(solutions_list) != len(answers_ground_truth):
            raise Exception("Number of answers lists must the same as the number of answers in the ground truth list.")

        output = []
        index = 0
        for solutions in solutions_list:
            if not isinstance(solutions, list):
                if isinstance(solutions, str):
                    solutions = [solutions]
                else:
                    raise Exception("Each item in answers_list must be a list of answers or an answer.")
            answers = Challenger.extract_answers(solutions)
            total_count = len(answers)
            count = 0
            for ans in answers:
                if ans == str(answers_ground_truth[index]):
                    count += 1
            output.append(count / total_count)
            index += 1

        return output
/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnswerChoiceCreateSchema } from './AnswerChoiceCreateSchema';
import type { QuestionTagSchema } from './QuestionTagSchema';
export type QuestionUpdateSchema = {
    /**
     * The text of the question
     */
    text?: (string | null);
    /**
     * ID of the subject associated with the question
     */
    subject_id?: (number | null);
    /**
     * ID of the topic associated with the question
     */
    topic_id?: (number | null);
    /**
     * ID of the subtopic associated with the question
     */
    subtopic_id?: (number | null);
    /**
     * The difficulty level of the question
     */
    difficulty?: (string | null);
    /**
     * A list of answer choices
     */
    answer_choices?: (Array<AnswerChoiceCreateSchema> | null);
    /**
     * A list of tags associated with the question
     */
    tags?: (Array<QuestionTagSchema> | null);
    /**
     * Updated list of question set IDs the question belongs to
     */
    question_set_ids?: (Array<number> | null);
};


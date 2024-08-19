/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnswerChoiceSchema } from './AnswerChoiceSchema';
import type { QuestionTagSchema } from './QuestionTagSchema';
export type QuestionSchema = {
    text: string;
    subject_id: number;
    topic_id: number;
    subtopic_id: number;
    id: number;
    difficulty?: (string | null);
    tags?: (Array<QuestionTagSchema> | null);
    answer_choices?: Array<AnswerChoiceSchema>;
    question_set_ids?: (Array<number> | null);
};


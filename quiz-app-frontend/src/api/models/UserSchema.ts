/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GroupSchema } from './GroupSchema';
import type { QuestionSetSchema } from './QuestionSetSchema';
export type UserSchema = {
    username: string;
    email: string;
    role: string;
    id: number;
    is_active: boolean;
    is_admin: boolean;
    group_ids?: Array<GroupSchema>;
    created_groups?: Array<GroupSchema>;
    created_question_sets?: Array<QuestionSetSchema>;
};


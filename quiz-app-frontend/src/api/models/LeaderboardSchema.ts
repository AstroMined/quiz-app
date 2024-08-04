/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TimePeriodModel } from './TimePeriodModel';
export type LeaderboardSchema = {
    id: number;
    user_id: number;
    score: number;
    time_period: TimePeriodModel;
    group_id?: (number | null);
};


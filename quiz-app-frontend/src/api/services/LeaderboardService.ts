/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LeaderboardSchema } from '../models/LeaderboardSchema';
import type { TimePeriodModel } from '../models/TimePeriodModel';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LeaderboardService {
    /**
     * Get Leaderboard
     * @param timePeriod
     * @param groupId
     * @param limit
     * @returns LeaderboardSchema Successful Response
     * @throws ApiError
     */
    public static getLeaderboardLeaderboardGet(
        timePeriod: TimePeriodModel,
        groupId?: number,
        limit: number = 10,
    ): CancelablePromise<Array<LeaderboardSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/leaderboard/',
            query: {
                'time_period': timePeriod,
                'group_id': groupId,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

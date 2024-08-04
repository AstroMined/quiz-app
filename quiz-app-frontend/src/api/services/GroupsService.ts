/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GroupSchema } from '../models/GroupSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GroupsService {
    /**
     * Create Group Endpoint
     * @param requestBody
     * @returns GroupSchema Successful Response
     * @throws ApiError
     */
    public static createGroupEndpointGroupsPost(
        requestBody: Record<string, any>,
    ): CancelablePromise<GroupSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/groups',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Group Endpoint
     * @param groupId
     * @returns GroupSchema Successful Response
     * @throws ApiError
     */
    public static getGroupEndpointGroupsGroupIdGet(
        groupId: number,
    ): CancelablePromise<GroupSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Group Endpoint
     * @param groupId
     * @param requestBody
     * @returns GroupSchema Successful Response
     * @throws ApiError
     */
    public static updateGroupEndpointGroupsGroupIdPut(
        groupId: number,
        requestBody: Record<string, any>,
    ): CancelablePromise<GroupSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Group Endpoint
     * @param groupId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteGroupEndpointGroupsGroupIdDelete(
        groupId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

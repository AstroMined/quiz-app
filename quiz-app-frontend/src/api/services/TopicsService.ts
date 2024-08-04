/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TopicCreateSchema } from '../models/TopicCreateSchema';
import type { TopicSchema } from '../models/TopicSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TopicsService {
    /**
     * Create Topic Endpoint
     * Create a new topic.
     *
     * Args:
     * topic (TopicCreateSchema): The topic data to be created.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * TopicSchema: The created topic.
     * @param requestBody
     * @returns TopicSchema Successful Response
     * @throws ApiError
     */
    public static createTopicEndpointTopicsPost(
        requestBody: TopicCreateSchema,
    ): CancelablePromise<TopicSchema> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/topics/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Read Topic Endpoint
     * Read a topic by its ID.
     *
     * Args:
     * topic_id (int): The ID of the topic to be read.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * TopicSchema: The read topic.
     *
     * Raises:
     * HTTPException: If the topic is not found.
     * @param topicId
     * @returns TopicSchema Successful Response
     * @throws ApiError
     */
    public static readTopicEndpointTopicsTopicIdGet(
        topicId: number,
    ): CancelablePromise<TopicSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/topics/{topic_id}',
            path: {
                'topic_id': topicId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Topic Endpoint
     * Update a topic by its ID.
     *
     * Args:
     * topic_id (int): The ID of the topic to be updated.
     * topic (TopicCreateSchema): The updated topic data.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Returns:
     * TopicSchema: The updated topic.
     *
     * Raises:
     * HTTPException: If the topic is not found.
     * @param topicId
     * @param requestBody
     * @returns TopicSchema Successful Response
     * @throws ApiError
     */
    public static updateTopicEndpointTopicsTopicIdPut(
        topicId: number,
        requestBody: TopicCreateSchema,
    ): CancelablePromise<TopicSchema> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/topics/{topic_id}',
            path: {
                'topic_id': topicId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Topic Endpoint
     * Delete a topic by its ID.
     *
     * Args:
     * topic_id (int): The ID of the topic to be deleted.
     * db (Session, optional): The database session. Defaults to Depends(get_db).
     *
     * Raises:
     * HTTPException: If the topic is not found.
     * @param topicId
     * @returns void
     * @throws ApiError
     */
    public static deleteTopicEndpointTopicsTopicIdDelete(
        topicId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/topics/{topic_id}',
            path: {
                'topic_id': topicId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

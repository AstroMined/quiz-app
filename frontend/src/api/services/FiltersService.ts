/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { QuestionSchema } from '../models/QuestionSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FiltersService {
    /**
     * Filter Questions Endpoint
     * This function filters questions based on the provided parameters.
     * Returns a list of questions that match the filters.
     *
     * Parameters:
     * ----------
     * request: Request
     * The request object containing all the parameters.
     * subject: Optional[str]
     * The subject to filter the questions by.
     * topic: Optional[str]
     * The topic to filter the questions by.
     * subtopic: Optional[str]
     * The subtopic to filter the questions by.
     * difficulty: Optional[str]
     * The difficulty level to filter the questions by.
     * tags: Optional[List[str]]
     * The tags to filter the questions by.
     * db: Session
     * The database session.
     * skip: int
     * The number of records to skip.
     * limit: int
     * The maximum number of records to return.
     *
     * Returns:
     * ----------
     * List[QuestionSchema]
     * A list of questions that match the filters.
     * @param subject
     * @param topic
     * @param subtopic
     * @param difficulty
     * @param tags
     * @param skip
     * @param limit
     * @returns QuestionSchema Successful Response
     * @throws ApiError
     */
    public static filterQuestionsEndpointQuestionsFilterGet(
        subject?: (string | null),
        topic?: (string | null),
        subtopic?: (string | null),
        difficulty?: (string | null),
        tags?: (Array<string> | null),
        skip?: number,
        limit: number = 100,
    ): CancelablePromise<Array<QuestionSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/questions/filter',
            query: {
                'subject': subject,
                'topic': topic,
                'subtopic': subtopic,
                'difficulty': difficulty,
                'tags': tags,
                'skip': skip,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}

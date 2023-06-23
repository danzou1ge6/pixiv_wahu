import {wahuRPCCall} from "./client"

export type Path = string
export type datetime = string
export type PixivRecomMode = 'day' | 'week' | 'month' | 'day_male' | 'day_female' | 'week_original' | 'week_rookie'
export type PixivSearchTarget = 'partial_match_for_tags' | 'exact_match_for_tags' | 'title_and_caption' | 'keyword'
export type PixivSort = 'date_desc' | 'date_asc' | 'popular_desc'

interface PixivComment {
    cid: number;
    comment: string;
    date: string;
    user: PixivUserSummery;
    parent_cid: number | null;
}

interface PixivUserSummery {
    account: string;
    uid: number;
    is_followed: boolean;
    name: string;
    profile_image: string;
}

interface IllustTag {
    name: string;
    translated: string;
}

interface IllustDetail {
    iid: number;
    title: string;
    caption: string;
    height: number;
    width: number;
    is_bookmarked: boolean;
    is_muted: boolean;
    page_count: number;
    restrict: number;
    sanity_level: number;
    tags: Array<IllustTag>;
    total_bookmarks: number;
    type: string;
    total_view: number;
    user: PixivUserSummery;
    visible: boolean;
    x_restrict: number;
    image_origin: Array<string>;
    image_large: Array<string>;
    image_medium: Array<string>;
    image_sqmedium: Array<string>;
}

interface PixivUserDetail {
    uid: number;
    account: string;
    name: string;
    profile_image: string;
    is_followed: boolean;
    comment: string;
    total_followers: number;
    total_mypixiv_users: number;
    total_illusts: number;
    total_manga: number;
    total_novels: number;
    total_bookmarked_illust: number;
    background_image: string;
}

interface PixivUserPreview {
    user_summery: PixivUserSummery;
    illusts: Array<IllustDetail>;
}

interface IllustBookmark {
    iid: number;
    pages: Array<number>;
    add_timestamp: number;
}

interface FileEntry {
    path: Path;
    fid: string;
}

interface TrendingTagIllusts {
    tag: IllustTag;
    illust: IllustDetail;
}

interface FileTracingConfig {
    ftid: number;
    name: string;
    ignore: Array<string>;
}

interface RepoSyncAddReport {
    db_name: string;
    entries: Array<FileEntryWithURL>;
}

interface AccountSession {
    user_name: string;
    user_id: number;
    expire_at: datetime;
    access_token: string;
}

interface FileEntryWithURL {
    path: Path;
    fid: string;
    url: string;
}

interface DownloadProgress {
    gid: string;
    total_size: number | null;
    downloaded_size: number;
    descript: string | null;
    status: 'inprogress' | 'finished' | 'error' | 'pending';
}

interface CliScriptInfo {
    path: Path;
    name: string;
    descrip: string;
    code: string;
}

interface WeighedIllustTag {
    name: string;
    translated: string;
    weight: number;
}

interface CountedIllustTag {
    name: string;
    translated: string;
    count: number;
}

interface TagRegressionModel {
    weighed_tags: Array<WeighedIllustTag>;
    bias: number;
}

interface IllustBookmarkingConfig {
    did: number;
    name: string;
    description: string;
    subscribed_user_uid: Array<number>;
    subscribed_bookmark_uid: Array<number>;
    subscribe_overwrite: 'intelligent' | 'append' | 'replace';
    subscribe_pages: number;
}

export type {PixivComment, PixivUserSummery, IllustTag, IllustDetail, PixivUserDetail, PixivUserPreview, IllustBookmark, FileEntry, TrendingTagIllusts, FileTracingConfig, RepoSyncAddReport, AccountSession, FileEntryWithURL, DownloadProgress, CliScriptInfo, WeighedIllustTag, CountedIllustTag, TagRegressionModel, IllustBookmarkingConfig}

export async function cli_list () : Promise<Array<CliScriptInfo>> {
    return await wahuRPCCall('cli_list', [])as Array<CliScriptInfo>}

export async function cli_open_editor (name: string) : Promise<null> {
    return await wahuRPCCall('cli_open_editor', [name])as null}

export async function cli_reload () : Promise<null> {
    return await wahuRPCCall('cli_reload', [])as null}

export async function download_image (url: string, path: Path) : Promise<null> {
    return await wahuRPCCall('download_image', [url, path])as null}

export async function filename_for_illust (dtl: IllustDetail, pages: Array<number>) : Promise<Array<string>> {
    return await wahuRPCCall('filename_for_illust', [dtl, pages])as Array<string>}

export async function get_config (name: string) : Promise<string> {
    return await wahuRPCCall('get_config', [name])as string}

export async function ibd_copy (name: string, target: string, iids: Array<number>) : Promise<null> {
    return await wahuRPCCall('ibd_copy', [name, target, iids])as null}

export async function ibd_export_json (name: string) : Promise<string> {
    return await wahuRPCCall('ibd_export_json', [name])as string}

export async function ibd_filter_restricted (name: string) : Promise<Array<number>> {
    return await wahuRPCCall('ibd_filter_restricted', [name])as Array<number>}

export async function ibd_fuzzy_query (name: string, target: 'title' | 'caption' | 'tag' | 'username', keyword: string, cutoff: null | number) : Promise<Array<[number, number]>> {
    return await wahuRPCCall('ibd_fuzzy_query', [name, target, keyword, cutoff])as Array<[number, number]>}

export async function ibd_get_config (name: string) : Promise<IllustBookmarkingConfig> {
    return await wahuRPCCall('ibd_get_config', [name])as IllustBookmarkingConfig}

export async function ibd_ilst_count (name: string) : Promise<number> {
    return await wahuRPCCall('ibd_ilst_count', [name])as number}

export async function ibd_ilst_detail (name: string, iid: number) : Promise<null | IllustDetail> {
    return await wahuRPCCall('ibd_ilst_detail', [name, iid])as null | IllustDetail}

export async function ibd_import_json (name: string, json_str: string) : Promise<null> {
    return await wahuRPCCall('ibd_import_json', [name, json_str])as null}

export async function ibd_list () : Promise<Array<string>> {
    return await wahuRPCCall('ibd_list', [])as Array<string>}

export async function ibd_list_bm (name: string) : Promise<Array<IllustBookmark>> {
    return await wahuRPCCall('ibd_list_bm', [name])as Array<IllustBookmark>}

export async function ibd_new (name: string) : Promise<null> {
    return await wahuRPCCall('ibd_new', [name])as null}

export async function ibd_query (name: string, qs: string) : Promise<Array<[number, number]>> {
    return await wahuRPCCall('ibd_query', [name, qs])as Array<[number, number]>}

export async function ibd_query_bm (name: string, iid: number) : Promise<null | IllustBookmark> {
    return await wahuRPCCall('ibd_query_bm', [name, iid])as null | IllustBookmark}

export async function ibd_query_help () : Promise<string> {
    return await wahuRPCCall('ibd_query_help', [])as string}

export async function ibd_query_uid (name: string, uid: number) : Promise<Array<number>> {
    return await wahuRPCCall('ibd_query_uid', [name, uid])as Array<number>}

export async function ibd_remove (name: string) : Promise<null> {
    return await wahuRPCCall('ibd_remove', [name])as null}

export async function ibd_set_bm (name: string, iid: number, pages: Array<number>) : Promise<[boolean, boolean]> {
    return await wahuRPCCall('ibd_set_bm', [name, iid, pages])as [boolean, boolean]}

export async function ibd_set_config (name: string, config: IllustBookmarkingConfig) : Promise<null> {
    return await wahuRPCCall('ibd_set_config', [name, config])as null}

export async function ibd_update (name: string) : Promise<null> {
    return await wahuRPCCall('ibd_update', [name])as null}

export async function ibd_update_subs (name: string, page_num: null | number) : Promise<AsyncGenerator<string, undefined, null | string>> {
    return await wahuRPCCall('ibd_update_subs', [name, page_num])as AsyncGenerator<string, undefined, null | string>}

export async function ibdtag_count (names: Array<string>) : Promise<Array<CountedIllustTag>> {
    return await wahuRPCCall('ibdtag_count', [names])as Array<CountedIllustTag>}

export async function ibdtag_logistic_regression (pos: Array<string>, neg: Array<string>, tags: Array<IllustTag>, lr: number, batch_size: number, epoch: number, test_set_ratio: number) : Promise<AsyncGenerator<[[number, number], null | [Array<number>, Array<number>, TagRegressionModel]], undefined, null>> {
    return await wahuRPCCall('ibdtag_logistic_regression', [pos, neg, tags, lr, batch_size, epoch, test_set_ratio])as AsyncGenerator<[[number, number], null | [Array<number>, Array<number>, TagRegressionModel]], undefined, null>}

export async function ibdtag_write_model (model: TagRegressionModel, model_name: string) : Promise<null> {
    return await wahuRPCCall('ibdtag_write_model', [model, model_name])as null}

export async function ir_add_cache (name: string, file_entries: Array<FileEntry>) : Promise<null> {
    return await wahuRPCCall('ir_add_cache', [name, file_entries])as null}

export async function ir_calc_sync (name: string) : Promise<[Array<FileEntry>, Array<RepoSyncAddReport>]> {
    return await wahuRPCCall('ir_calc_sync', [name])as [Array<FileEntry>, Array<RepoSyncAddReport>]}

export async function ir_download (name: string, file_entries_withurl: Array<FileEntryWithURL>) : Promise<null> {
    return await wahuRPCCall('ir_download', [name, file_entries_withurl])as null}

export async function ir_empty_cache (name: string) : Promise<null> {
    return await wahuRPCCall('ir_empty_cache', [name])as null}

export async function ir_get_cache (name: string) : Promise<Array<FileEntry>> {
    return await wahuRPCCall('ir_get_cache', [name])as Array<FileEntry>}

export async function ir_get_index (name: string) : Promise<Array<FileEntry>> {
    return await wahuRPCCall('ir_get_index', [name])as Array<FileEntry>}

export async function ir_linked_db (name: string) : Promise<Array<string>> {
    return await wahuRPCCall('ir_linked_db', [name])as Array<string>}

export async function ir_list () : Promise<Array<string>> {
    return await wahuRPCCall('ir_list', [])as Array<string>}

export async function ir_new (name: string, prefix: string) : Promise<null> {
    return await wahuRPCCall('ir_new', [name, prefix])as null}

export async function ir_remove (name: string) : Promise<null> {
    return await wahuRPCCall('ir_remove', [name])as null}

export async function ir_remove_file (name: string, files: Array<Path>) : Promise<null> {
    return await wahuRPCCall('ir_remove_file', [name, files])as null}

export async function ir_rm_index (name: string, index_fids: Array<string>) : Promise<null> {
    return await wahuRPCCall('ir_rm_index', [name, index_fids])as null}

export async function ir_set_linked_db (name: string, db_names: Array<string>) : Promise<null> {
    return await wahuRPCCall('ir_set_linked_db', [name, db_names])as null}

export async function ir_update_index (name: string) : Promise<Array<FileEntry>> {
    return await wahuRPCCall('ir_update_index', [name])as Array<FileEntry>}

export async function ir_validate (name: string) : Promise<[Array<FileEntry>, Array<Path>]> {
    return await wahuRPCCall('ir_validate', [name])as [Array<FileEntry>, Array<Path>]}

export async function p_account_session () : Promise<null | AccountSession> {
    return await wahuRPCCall('p_account_session', [])as null | AccountSession}

export async function p_attempt_login () : Promise<AccountSession> {
    return await wahuRPCCall('p_attempt_login', [])as AccountSession}

export async function p_ilst_detail (iid: number) : Promise<IllustDetail> {
    return await wahuRPCCall('p_ilst_detail', [iid])as IllustDetail}

export async function p_ilst_folow () : Promise<AsyncGenerator<Array<IllustDetail>, undefined, null>> {
    return await wahuRPCCall('p_ilst_folow', [])as AsyncGenerator<Array<IllustDetail>, undefined, null>}

export async function p_ilst_new () : Promise<AsyncGenerator<Array<IllustDetail>, undefined, null>> {
    return await wahuRPCCall('p_ilst_new', [])as AsyncGenerator<Array<IllustDetail>, undefined, null>}

export async function p_ilst_ranking (mode: PixivRecomMode) : Promise<AsyncGenerator<Array<IllustDetail>, undefined, null>> {
    return await wahuRPCCall('p_ilst_ranking', [mode])as AsyncGenerator<Array<IllustDetail>, undefined, null>}

export async function p_ilst_recom () : Promise<AsyncGenerator<Array<IllustDetail>, undefined, null>> {
    return await wahuRPCCall('p_ilst_recom', [])as AsyncGenerator<Array<IllustDetail>, undefined, null>}

export async function p_ilst_related (iid: number) : Promise<AsyncGenerator<Array<IllustDetail>, undefined, null>> {
    return await wahuRPCCall('p_ilst_related', [iid])as AsyncGenerator<Array<IllustDetail>, undefined, null>}

export async function p_ilst_search (keyword: string, target: null | PixivSearchTarget, sort: null | PixivSort) : Promise<AsyncGenerator<Array<IllustDetail>, undefined, null>> {
    return await wahuRPCCall('p_ilst_search', [keyword, target, sort])as AsyncGenerator<Array<IllustDetail>, undefined, null>}

export async function p_ilstbm_add (iids: Array<number>) : Promise<null> {
    return await wahuRPCCall('p_ilstbm_add', [iids])as null}

export async function p_ilstbm_rm (iids: Array<number>) : Promise<null> {
    return await wahuRPCCall('p_ilstbm_rm', [iids])as null}

export async function p_query (qs: string) : Promise<AsyncGenerator<Array<[IllustDetail, number]>, undefined, null>> {
    return await wahuRPCCall('p_query', [qs])as AsyncGenerator<Array<[IllustDetail, number]>, undefined, null>}

export async function p_query_help () : Promise<string> {
    return await wahuRPCCall('p_query_help', [])as string}

export async function p_query_user (qs: string) : Promise<AsyncGenerator<Array<PixivUserPreview>, undefined, null> | number> {
    return await wahuRPCCall('p_query_user', [qs])as AsyncGenerator<Array<PixivUserPreview>, undefined, null> | number}

export async function p_query_user_help () : Promise<string> {
    return await wahuRPCCall('p_query_user_help', [])as string}

export async function p_trending_tags () : Promise<Array<TrendingTagIllusts>> {
    return await wahuRPCCall('p_trending_tags', [])as Array<TrendingTagIllusts>}

export async function p_user_bmilsts (uid: number) : Promise<AsyncGenerator<Array<IllustDetail>, undefined, null>> {
    return await wahuRPCCall('p_user_bmilsts', [uid])as AsyncGenerator<Array<IllustDetail>, undefined, null>}

export async function p_user_detail (uid: number) : Promise<PixivUserDetail> {
    return await wahuRPCCall('p_user_detail', [uid])as PixivUserDetail}

export async function p_user_follow_add (uid: number) : Promise<null> {
    return await wahuRPCCall('p_user_follow_add', [uid])as null}

export async function p_user_follow_rm (uid: number) : Promise<null> {
    return await wahuRPCCall('p_user_follow_rm', [uid])as null}

export async function p_user_follower (uid: number) : Promise<AsyncGenerator<Array<PixivUserPreview>, undefined, null>> {
    return await wahuRPCCall('p_user_follower', [uid])as AsyncGenerator<Array<PixivUserPreview>, undefined, null>}

export async function p_user_following (uid: number) : Promise<AsyncGenerator<Array<PixivUserPreview>, undefined, null>> {
    return await wahuRPCCall('p_user_following', [uid])as AsyncGenerator<Array<PixivUserPreview>, undefined, null>}

export async function p_user_ilsts (uid: number) : Promise<AsyncGenerator<Array<IllustDetail>, undefined, null>> {
    return await wahuRPCCall('p_user_ilsts', [uid])as AsyncGenerator<Array<IllustDetail>, undefined, null>}

export async function p_user_related (uid: number) : Promise<AsyncGenerator<Array<PixivUserPreview>, undefined, null>> {
    return await wahuRPCCall('p_user_related', [uid])as AsyncGenerator<Array<PixivUserPreview>, undefined, null>}

export async function p_user_search (keyword: string) : Promise<AsyncGenerator<Array<PixivUserPreview>, undefined, null>> {
    return await wahuRPCCall('p_user_search', [keyword])as AsyncGenerator<Array<PixivUserPreview>, undefined, null>}

export async function token_get_loginurl () : Promise<string> {
    return await wahuRPCCall('token_get_loginurl', [])as string}

export async function token_submit_code (code: string) : Promise<string> {
    return await wahuRPCCall('token_submit_code', [code])as string}

export async function wahu_anext (key: string, send_val: any) : Promise<null | any> {
    return await wahuRPCCall('wahu_anext', [key, send_val])as null | any}

export async function wahu_cli_complete (cmd: string) : Promise<Array<string>> {
    return await wahuRPCCall('wahu_cli_complete', [cmd])as Array<string>}

export async function wahu_client_exec (args: Array<string>, term_size: [number, number]) : Promise<AsyncGenerator<string, undefined, null | string>> {
    return await wahuRPCCall('wahu_client_exec', [args, term_size])as AsyncGenerator<string, undefined, null | string>}

export async function wahu_dispose_generator (key: string) : Promise<boolean> {
    return await wahuRPCCall('wahu_dispose_generator', [key])as boolean}

export async function wahu_dl_status () : Promise<Array<DownloadProgress>> {
    return await wahuRPCCall('wahu_dl_status', [])as Array<DownloadProgress>}

export async function wahu_download (iids: Array<number>) : Promise<null> {
    return await wahuRPCCall('wahu_download', [iids])as null}

export async function wahu_exec (cmd: string) : Promise<AsyncGenerator<string, undefined, null | string>> {
    return await wahuRPCCall('wahu_exec', [cmd])as AsyncGenerator<string, undefined, null | string>}

export async function wahu_logger_client () : Promise<AsyncGenerator<[number, string], undefined, null>> {
    return await wahuRPCCall('wahu_logger_client', [])as AsyncGenerator<[number, string], undefined, null>}


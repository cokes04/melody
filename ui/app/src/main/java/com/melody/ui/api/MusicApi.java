package com.melody.ui.api;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.POST;

public interface MusicApi {
    String GENERATE_BASE_URL = "https://jqm4lisgm0.execute-api.ap-northeast-2.amazonaws.com";

    @POST("/Prod/music")
    Call<GenerateMusicResponse> generateMusic(@Body GenerateMusicRequest request);
}

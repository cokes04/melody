package com.melody.ui.api;


import com.google.gson.annotations.SerializedName;

public class GenerateMusicResponse {
    @SerializedName("result")
    private boolean result;

    @SerializedName("message")
    private String message;

    @SerializedName("url")
    private String url;

    public GenerateMusicResponse() {
    }

    public GenerateMusicResponse(boolean result, String message, String url) {
        this.result = result;
        this.message = message;
        this.url = url;
    }

    public boolean isResult() {
        return result;
    }

    public String getUrl() {
        return url;
    }

    public void setResult(boolean result) {
        this.result = result;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    @Override
    public String toString() {
        return "GenerateMusicResponse{" +
                "result=" + result +
                ", message='" + message + '\'' +
                ", url='" + url + '\'' +
                '}';
    }
}

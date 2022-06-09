package com.melody.ui.api;


public class GenerateMusicRequest {
    private String emotion;

    private int noise_num;

    private int music_len;

    public GenerateMusicRequest() {
    }

    public GenerateMusicRequest(String emotion, int noise_num, int music_len) {
        this.emotion = emotion;
        this.noise_num = noise_num;
        this.music_len = music_len;
    }

    public void setEmotion(String emotion) {
        this.emotion = emotion;
    }

    public void setNoise_num(int noise_num) {
        this.noise_num = noise_num;
    }

    public void setMusic_len(int music_len) {
        this.music_len = music_len;
    }

    public String getEmotion() {
        return emotion;
    }

    public int getNoise_num() {
        return noise_num;
    }

    public int getMusic_len() {
        return music_len;
    }

    @Override
    public String toString() {
        return "GenerateMusicRequest{" +
                "emotion='" + emotion + '\'' +
                ", noise_num=" + noise_num +
                ", music_len=" + music_len +
                '}';
    }
}

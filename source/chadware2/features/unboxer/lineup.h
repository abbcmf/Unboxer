#pragma once

// The lineups: the team intro, the team select and the end of the match show every player as a character
// (C_CSGO_TeamPreviewCharacterPosition and the classes built on it - TeamSelect T/CT, TeamIntro T/CT, WingmanIntro,
// EndOfMatch). The server fills a position with your REAL agent, gloves and weapon; yours gets your Lootline agent,
// gloves and the Lootline skin of the weapon it holds instead. Only you see it. Lootline only.
namespace Lineup
{
    // The builder hook, on the thread the game builds on: before - your position's items become your Lootline ones
    // (only your own position, only what Lootline has something for); after - your character and its gun are queued
    // for FrameTick. SEH-guarded.
    void BeforeBuild(void* position);
    void AfterBuild(void* position);

    // FrameStageNotify, FRAME_NET_UPDATE_END (where the skin changer works): the skin changer's recipe on your lineup
    // character - the gun's skin material and the gloves' rebuild flag on 4 frames in a row and again 0.4 / 1.2 / 3 s
    // later, then the game's RegenerateSkins. SEH-guarded.
    void FrameTick();
}

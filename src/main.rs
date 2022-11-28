use std::fs;

use serenity::async_trait;
use serenity::prelude::*;
use serenity::framework::standard::macros::group;
use serenity::framework::standard::StandardFramework;

mod commands;
use crate::commands::scan::*;
use crate::commands::meta::*;

#[group]
#[commands(ping, scan)]
struct General;

struct Handler;

#[async_trait]
impl EventHandler for Handler {}

#[tokio::main]
async fn main() {
    let framework = StandardFramework::new()
        .configure(|c| c.prefix("pls ")) // set the bot's prefix to "pls "
        .group(&GENERAL_GROUP);

    // Read the bot token from the TOKEN file in the project's root
    let token: String = fs::read_to_string("TOKEN")
        .expect("Couldn't read TOKEN file")
        .parse().expect("Couldn't parse TOKEN file");

    let intents = GatewayIntents::non_privileged()
        | GatewayIntents::MESSAGE_CONTENT;

    let mut client = Client::builder(token, intents)
        .event_handler(Handler)
        .framework(framework)
        .await
        .expect("Error creating client");

    // start listening for events by starting a single shard
    if let Err(why) = client.start().await {
        println!("An error occurred while running the client: {:?}", why)
    }
}

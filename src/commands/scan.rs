// scan.rs //

// Get every message in the server so we can show cool analytics :)

use std::collections::HashMap;

use serenity::model::Timestamp;
use serenity::model::prelude::{ChannelId, MessageId};
use serenity::model::user::User;
use serenity::prelude::*;
use serenity::model::channel::Message;
use serenity::framework::standard::macros::command;
use serenity::framework::standard::CommandResult;
use serenity::futures::StreamExt;
use serenity::model::channel::MessagesIter;

struct MessageContent {
    id: MessageId,
    user: User,
    time: Timestamp,
}

impl MessageContent {
    fn new(id: MessageId, user: User, time: Timestamp) -> Self { Self { id, user, time } }
}

#[command]
pub async fn scan(ctx: &Context, msg: &Message) -> CommandResult {
    let typing = msg.channel_id.start_typing(&ctx.http).expect("Couldn't start typing indicator");

    // Initialise a list of messages by channel
    let mut map: HashMap<ChannelId, Vec<MessageContent>> = HashMap::new();

    // Get the guild's ID
    let id = msg.guild_id.unwrap();

    // Iterate over each channel in the guild...
    for (_, channel) in ctx.cache.guild_channels(id).unwrap() {
        // ensuring it's a text channel...
        if channel.is_text_based() {
            println!("Scanning {}...", channel.id.name(&ctx.cache).await.unwrap());

            // and get all messages in the channel, 100 at a time
            let mut vec: Vec<MessageContent> = Vec::new();

            let mut messages = channel.id.messages_iter(&ctx).boxed();
            while let Some(x) = messages.next().await {
                let message = x.expect("Couldn't get message");
                vec.push(MessageContent::new(message.id,
                                             message.author,
                                             message.timestamp));
            }

            // then put them into the map
            map.insert(channel.id, vec);
        }
    }

    typing.stop().unwrap();
    msg.reply(ctx, "finished scanning").await?;


    // testing code to make sure it worked
    for (id, messages) in map {
        println!("{} has {} messages", id.name(&ctx.cache).await.unwrap(), messages.len());
    }

    Ok(())
}

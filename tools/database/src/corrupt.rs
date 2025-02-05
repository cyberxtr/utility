use crate::utils::open_state_snapshot;
use anyhow::anyhow;
use clap::Parser;
use std::path::PathBuf;
use unc_primitives::shard_layout::{ShardLayout, ShardVersion};
use unc_store::{flat::FlatStorageManager, ShardUId, StoreUpdate};

#[derive(Parser)]
pub(crate) struct CorruptStateSnapshotCommand {
    #[clap(short, long)]
    shard_layout_version: ShardVersion,
}

impl CorruptStateSnapshotCommand {
    pub(crate) fn run(&self, home: &PathBuf) -> anyhow::Result<()> {
        let store = open_state_snapshot(home, unc_store::Mode::ReadWrite)?;
        let flat_storage_manager = FlatStorageManager::new(store.clone());

        let mut store_update = store.store_update();
        // TODO(resharding) automatically detect the shard version
        let shard_layout = match self.shard_layout_version {
            0 => ShardLayout::v0(1, 0),
            1 => ShardLayout::v0(1, 0),
            2 => ShardLayout::v0(1, 0),
            _ => {
                return Err(anyhow!(
                    "Unsupported shard layout version! {}",
                    self.shard_layout_version
                ))
            }
        };
        for shard_uid in shard_layout.shard_uids() {
            corrupt(&mut store_update, &flat_storage_manager, shard_uid)?;
        }
        store_update.commit().unwrap();

        println!("corrupted the state snapshot");

        Ok(())
    }
}

fn corrupt(
    store_update: &mut StoreUpdate,
    flat_storage_manager: &FlatStorageManager,
    shard_uid: ShardUId,
) -> Result<(), anyhow::Error> {
    flat_storage_manager.create_flat_storage_for_shard(shard_uid)?;
    let result = flat_storage_manager.remove_flat_storage_for_shard(shard_uid, store_update)?;
    println!("removed flat storage for shard {shard_uid:?} result is {result}");
    Ok(())
}

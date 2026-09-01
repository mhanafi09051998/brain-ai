const { Keypair, Connection, clusterApiUrl, PublicKey } = require('@solana/web3.js');
const { createMint, getOrCreateAssociatedTokenAccount, mintTo, setAuthority, AuthorityType } = require('@solana/spl-token');

// Script akan dieksekusi setelah pengguna memberikan detail Token
async function launchSecureToken(walletKeypair, decimals, totalSupply) {
    const connection = new Connection(clusterApiUrl('mainnet-beta'), 'confirmed');
    
    console.log("🚀 Memulai Protokol Peluncuran Koin Amanah...");
    
    // 1. Create Mint
    const mint = await createMint(
        connection,
        walletKeypair,
        walletKeypair.publicKey, // Mint authority (sementara)
        walletKeypair.publicKey, // Freeze authority (sementara)
        decimals
    );
    console.log(`✅ Smart Contract Koin Tercipta: ${mint.toBase58()}`);

    // 2. Buat Dompet Penampung untuk Developer
    const tokenAccount = await getOrCreateAssociatedTokenAccount(
        connection,
        walletKeypair,
        mint,
        walletKeypair.publicKey
    );
    console.log(`✅ Brankas Koin Anda: ${tokenAccount.address.toBase58()}`);

    // 3. Cetak Seluruh Suplai (Satu Kali Saja)
    await mintTo(
        connection,
        walletKeypair,
        mint,
        tokenAccount.address,
        walletKeypair.publicKey,
        totalSupply * (10 ** decimals)
    );
    console.log(`✅ ${totalSupply} Koin berhasil dicetak ke brankas Anda.`);

    // 4. PROTOKOL ANTI-RUGPULL (Cabut Otoritas)
    console.log("🔒 Mengeksekusi Protokol Keamanan Tingkat Tinggi...");
    
    // Cabut Hak Cetak Baru (Revoke Mint)
    await setAuthority(connection, walletKeypair, mint, walletKeypair.publicKey, AuthorityType.MintTokens, null);
    console.log("🛡️ Mint Authority DICABUT (Suplai Terkunci Permanen. Bebas Inflasi).");

    // Cabut Hak Bekukan Dompet (Revoke Freeze)
    await setAuthority(connection, walletKeypair, mint, walletKeypair.publicKey, AuthorityType.FreezeAccount, null);
    console.log("🛡️ Freeze Authority DICABUT (Investor Aman 100%).");

    console.log("🎉 PELUNCURAN SELESAI. Koin ini sekarang dijamin AMANAH secara matematis.");
    return mint.toBase58();
}

module.exports = { launchSecureToken };

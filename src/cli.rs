use std::io::Write;

pub async fn repl() {
    loop {
        // Initialize input buffer
        let mut command = String::new();
        
        // Write REPL prompt
        print!("soulfur> ");
        // Ensure prompt is displayed before input is requested
        std::io::stdout().flush().unwrap();

        // Capture input and load into buffer `command`
        std::io::stdin()
            .read_line(&mut command)
            .expect("whoops");
    }
}

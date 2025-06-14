/// Typestate module for compile-time state guarantees
/// 
/// This module defines marker types used throughout the application
/// to encode state transitions at the type level.

use std::marker::PhantomData;

/// Marker trait for session states
pub trait SessionState {}

/// Repository states
pub mod repo {
    use super::*;
    
    pub struct Clean;
    pub struct Dirty;
    pub struct Detached;
    
    impl SessionState for Clean {}
    impl SessionState for Dirty {}
    impl SessionState for Detached {}
}

/// Watcher states
pub mod watcher {
    use super::*;
    
    pub struct Running;
    pub struct Stopped;
    
    impl SessionState for Running {}
    impl SessionState for Stopped {}
}

/// Generic state container for zero-cost abstractions
pub struct State<T: SessionState> {
    _phantom: PhantomData<T>,
}

impl<T: SessionState> State<T> {
    pub fn new() -> Self {
        State {
            _phantom: PhantomData,
        }
    }
}

impl<T: SessionState> Default for State<T> {
    fn default() -> Self {
        Self::new()
    }
}
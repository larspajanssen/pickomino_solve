FROM rust:1.88-bookworm AS wasm-build
RUN rustup target add wasm32-unknown-unknown
RUN cargo install wasm-bindgen-cli --version 0.2.105
WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY solver ./solver
COPY wasm ./wasm
RUN cargo build --release --target wasm32-unknown-unknown -p pickomino-wasm
RUN wasm-bindgen target/wasm32-unknown-unknown/release/pickomino_wasm.wasm --target web --out-dir wasm/pkg

FROM node:24-bookworm AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend ./
COPY --from=wasm-build /src/wasm/pkg /wasm/pkg
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=frontend-build /app/dist /usr/share/nginx/html
COPY frontend/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
